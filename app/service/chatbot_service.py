from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from pydantic import BaseModel
from typing import List
from fastapi import HTTPException
from app.core.config import settings
from app.db.chatbot_database import create_database_chain, execute_query

class ChatbotInput(BaseModel):
    query: str

# Gemini
llm = ChatGoogleGenerativeAI(model=settings.MODEL, google_api_key=settings.API_KEY)

# OpenAI
# llm = ChatOpenAI(model_name=settings.MODEL, openai_api_key=settings.API_KEY)

chat_history = SQLChatMessageHistory(session_id="default", connection_string=settings.DATABASE_URL)
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=chat_history, return_messages=True, llm=llm)

prompt = PromptTemplate(
    input_variables=["query", "chat_history"],
    template="""
    Bạn là một trợ lý AI thông minh, chuyên gia về sản phẩm.

    **Nhiệm vụ của bạn là:**

    1.  **Tìm kiếm sản phẩm phù hợp nhất** với câu hỏi của người dùng.
    2.  **Truy vấn database:** Sử dụng câu lệnh SQL phù hợp (dựa trên prompt SQL được cung cấp) để truy vấn.
    3.  **Hiển thị thông tin:**
        - **Trả lời một cách trực tiếp, súc tích và thân thiện.**
        - **Nếu không tìm thấy sản phẩm phù hợp, hãy trả lời rằng "Không tìm thấy sản phẩm phù hợp."**

    Lịch sử hội thoại trước đó: {chat_history}
    Người dùng hỏi: {query}
    Trả lời:
    """
)

sql_chain, database = create_database_chain(llm, settings.DATABASE_URL)

# Danh sách từ khóa sản phẩm
product_keywords = ["sản phẩm", "tên sản phẩm", "giá", "mua", "tìm", "kiếm", "hỏi về", "loại", "mẫu", "nhãn hiệu", "hãng", "thương hiệu", "sữa", "vitamin"] # Thêm từ khóa của bạn

def get_response(query: str) -> str:
    try:
        # Kiểm tra xem câu hỏi có chứa từ khóa sản phẩm không
        is_product_query = any(keyword in query.lower() for keyword in product_keywords)

        if is_product_query: # Nếu là câu hỏi về sản phẩm, truy vấn database
            table_info = database.get_table_info()
            sql_query = sql_chain.llm_chain.run({"query": query, "table_info": table_info})
            db_result = execute_query(database, sql_query)
            print("db_result:", db_result)

            chat_history_data = memory.load_memory_variables({})
            chat_history = chat_history_data.get("chat_history", "")

            llm_chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
            response = llm_chain.run({"query": query, "chat_history": chat_history})
            memory.save_context({"query": query}, {"response": response})

            if db_result and response:
                formatted_db_result = ""
                for row in db_result:
                    item_name = row[1] if len(row) > 1 else "Không có tên"
                    image_url = row[2] if len(row) > 2 else None
                    price = row[3] if len(row) > 3 else None

                    formatted_db_result += f"- Tên: {item_name}\n"
                    if image_url:
                        formatted_db_result += f"  Hình ảnh: {image_url}\n"
                    if price:
                        formatted_db_result += f"  Giá: {price}\n"
                    formatted_db_result += "\n"

                return f"Kết quả tìm kiếm:\n{formatted_db_result}\nBot: {response}"
            elif response:
                return response
            else:
                return "Không tìm thấy thông tin phù hợp."

        else: # Nếu không phải câu hỏi về sản phẩm, trả lời chung chung
            chat_history_data = memory.load_memory_variables({})
            chat_history = chat_history_data.get("chat_history", "")

            general_prompt = PromptTemplate( # Prompt đơn giản cho hội thoại thông thường
                input_variables=["query", "chat_history"],
                template="""Bạn là một trợ lý AI thân thiện.
                Lịch sử hội thoại: {chat_history}
                Người dùng hỏi: {query}
                Trả lời: """
            )
            general_llm_chain = LLMChain(llm=llm, prompt=general_prompt, memory=memory)
            general_response = general_llm_chain.run({"query": query, "chat_history": chat_history})
            memory.save_context({"query": query}, {"response": general_response})
            return general_response


    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_chat_history() -> List[str]:
    return memory.load_memory_variables({}).get("chat_history", [])