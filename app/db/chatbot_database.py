from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from sqlalchemy import create_engine, text
import re
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def remove_markdown(query: str) -> str:
    """Loại bỏ markdown code fences khỏi truy vấn SQL."""
    query = re.sub(r"```sql|```", "", query).strip()
    return query


def create_database_chain(llm, database_url):
    """Tạo và trả về SQLDatabaseChain."""
    engine = create_engine(database_url, echo=True)
    database = SQLDatabase(engine, metadata=Base.metadata, include_tables=["productDetail"])

    sql_prompt = PromptTemplate(
        input_variables=["query", "table_info"],
        template="""
            Bạn là một chuyên gia SQL và có thể trả lời các câu hỏi về database "products".
            Bạn có quyền truy cập thông tin sau về database:
            {table_info}

            **Bạn CHỈ được phép sử dụng bảng sau:**
            - **public."productDetail":** Chứa thông tin chi tiết về sản phẩm. Các cột quan trọng: `id`, `name` (tên sản phẩm), `image` (dạng url chứa hình ảnh sản phẩm), `"paymentPrice"` (giá sản phẩm).

            **Khi người dùng hỏi về sản phẩm, hãy làm theo các bước sau:**

            1.  **Tìm kiếm trực tiếp trong bảng `public."productDetail"`** cột `name` để tìm **sản phẩm phù hợp nhất** với câu hỏi của người dùng.
            2.  **Câu lệnh SQL có thể là:**
                - `SELECT id, name, image, "paymentPrice" FROM public."productDetail" WHERE name LIKE '%từ_khóa_sản_phẩm%';`
                ...
                **Chỉ trả về các cột `id`, `name`, `image` và `"paymentPrice"` từ bảng `public."productDetail"`.**

            Dựa trên database "products" và thông tin cột ở trên, hãy tạo ra câu lệnh SQL để trả lời câu hỏi sau:
            {query}
            Chỉ trả về câu lệnh SQL, không có bất cứ giải thích hoặc markdown nào khác.
        """
    )

    sql_llm_chain = LLMChain(llm=llm, prompt=sql_prompt)
    database_chain = SQLDatabaseChain(llm_chain=sql_llm_chain, database=database, verbose=True)
    return database_chain, database

def execute_query(database, query: str) -> str:
    """Thực thi truy vấn SQL và trả về kết quả đã định dạng."""
    cleaned_query = remove_markdown(query)
    engine = database._engine

    try:
        with engine.connect() as connection:
            result = connection.execute(text(cleaned_query))
            db_result = result.fetchall()

        return db_result
    except Exception as e:
        return f"Lỗi khi thực thi truy vấn SQL: {e}"