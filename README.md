![Packagist Dependency Version](https://img.shields.io/badge/python-3.11.6-blue?style=flat-square&logo=blue)
![Packagist Version](https://img.shields.io/badge/packagist-1.0-brightgreen?style=flat-square)
![Language Support](https://img.shields.io/badge/language-vietnamese-red?style=flat-square)

Chatbot AI
===
Đây là Chatbot AI có thể đưa ra gợi ý về sản phẩm dựa trên bộ dữ liệu người dùng cung cấp cho nó.
## Chức năng
- Tự động sàng lọc ra những sản phẩm phù hợp với yêu cầu của người dùng.
- Đưa ra câu trả lời về các sản phẩm dựa trên yêu cầu của người dùng.

## Cài đặt môi trường
- [PostgreSQL](https://www.postgresql.org)
- [Python 3.11.6](https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe)
- [Visual Studio Code](https://code.visualstudio.com/)
- Khởi động terminal và trỏ vào thư mục dự án: VD: d:/projects/hi1-chatbot.
- Chạy câu lệnh sau để cài đặt requirements:
  ```
  pip install -r requirements.txt
  ```

## Khởi tạo thông tin ban đầu cho AI
- Trong file **.env**:
  ```
  OPENAI_KEY = ""
  MODEL = ""
  ```
  Hãy điền thông tin tương ứng cho API key của bạn vào trong dấu **" "** của OPENAI_KEY và model của AI vào trong dấu **" "** của MODEL.

- Trong file **app/service/chatbot_service.py**, bạn tìm đoạn lệnh như sau:
  ```
  # Gemini
  llm = ChatGoogleGenerativeAI(model=settings.MODEL, google_api_key=settings.API_KEY)

  # OpenAI
  # llm = ChatOpenAI(model_name=settings.MODEL, openai_api_key=settings.API_KEY)
  ```
  Nếu bạn sử dụng Gemini, giữ nguyên phần này, nếu bạn sử dụng OpenAI hoặc các AI tương thích với client của OpenAI, thay đổi code phần này như sau:
  ```
  # Gemini
  # llm = ChatGoogleGenerativeAI(model=settings.MODEL, google_api_key=settings.API_KEY)

  # OpenAI
  llm = ChatOpenAI(model_name=settings.MODEL, openai_api_key=settings.API_KEY)
  ```
## Khởi tạo thông tin cho bộ dữ liệu
- Chỉnh sửa kết nối đến database của PostgreSQL trong file **.env**:
  ```
  DB_NAME=<tên database>
  DB_USER=<tên user>
  DB_PASSWORD=<mật khẩu>
  DB_HOST=<host>
  DB_PORT=<cổng kết nối>
  TB_NAME=<tên bảng>
  ```

- ***Trong trường hợp bạn chưa có database, bạn có thể khởi tạo database bằng cách:***

  - Chỉnh **DB_NAME** theo tên database bạn muốn tạo.

  - Chỉnh **TB_NAME** theo tên table bạn muốn tạo.

  - Chỉnh sửa dữ liệu theo ý muốn trong file **app/db/model.py** hoặc để nguyên theo mẫu có sẵn ( gồm id, tên, danh mục, màu sắc và giá tiền ).
  
  - Thêm lệnh sau để khởi tạo database:
    ```
    python -m app.db.database_create
    ```
    Nếu kết quả báo thành công, bạn có thể vào kiểm tra trong PostgreSQL để kiểm tra nó đã tạo một database mới chưa.

  - Thêm lệnh sau để khởi tạo bộ tạo dữ liệu tự động (các lệnh này bạn chỉ cần làm một lần nếu đây là lần đầu tiên bạn sinh bộ tạo dữ liệu):
    ```
    alembic init alembic
    ```
  - Chương trình sẽ tạo ra file **alembic.ini** và folder **alembic**.
  - Bạn cần vào file **alembic.ini**, tìm dòng code sau:
    ```
    sqlalchemy.url = driver://user:pass@localhost/dbname
    ```
    và xoá nó đi.

  - Tiếp theo vào folder **alembic** và tìm file **env.py**, xoá toàn bộ code trong file đó và thay bằng code sau:
    ```
    import os
    from logging.config import fileConfig
    from sqlalchemy import engine_from_config, pool
    from alembic import context
    from app.core.config import settings
    from app.db.model import Base  
    config = context.config

    if config.config_file_name is not None:
        fileConfig(config.config_file_name)

    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    target_metadata = Base.metadata

    def run_migrations_offline() -> None:
        """Run migrations in 'offline' mode."""
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online() -> None:
        """Run migrations in 'online' mode."""
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()

    ```
    - Tiếp đó chạy dòng lệnh sau trong terminal:
    ```
    alembic revision --autogenerate -m "initial migration"
    ```

  - Chạy dòng lệnh sau để chương trình tự sinh một bảng đặt theo **TB_NAME** trong file .env của bạn
    ```
    alembic upgrade head
    ```
  - Tiếp theo nếu bạn muốn tự sinh một bộ dữ liệu ngẫu nhiên, bạn chạy dòng lệnh này trong terminal:
    ```
    python -m app.db.database_seeder
    ```
    ### <ins>**Lưu ý**</ins>: 
  - Ở đây là bộ sinh tự sinh dữ liệu đang theo các trường dữ liệu có sẵn, nếu **model.py** của bạn có khác so với mẫu có sẵn, hãy sửa nội dung trong file **app/db/database_seeder.py** cho phù hợp với yêu cầu của bạn.

  - Bạn có thể kiểm tra dữ liệu đã được sinh ra trong PostgreSQL bằng câu lệnh:
    ```sql
    SELECT * FROM public.<TB_NAME>
    ```

## Khởi chạy chương trình
- Đầu tiên ta cần khởi tạo kết nối đến FastAPI:
  ```
  uvicorn app.main:app --reload
  ```
- Sau khi bạn thấy các dòng lệnh như sau:
  ```
  INFO:     Started server process [17648]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  ```
  tức là FastAPI đã được khởi tạo thành công.

- Tiếp đó bạn chạy lệnh sau:

  ```
  python -m test_bot
  ```
- Nếu gọi đúng, chương trình sẽ hiển thị như sau:
  ```
  Nhập 'exit' để thoát
  Bạn:
  ```
  Nhập câu truy vấn của bạn, ví dụ:
  ```
  Nhập 'exit' để thoát
  Bạn: Tôi cần tìm hai sản phẩm là đồ chơi có tổng giá dưới 500
  ```
  Sau đó bot sẽ trả lời lại cho bạn ví dụ như:
  ```
  Nhập 'exit' để thoát
  Bạn: các sản phẩm về golf

  Bot: Kết quả tìm kiếm:
  - Tên: Túi gậy golf
    Hình ảnh: https://admin.hi1.vn/uploads/tuiGolfCoBanhXeNu2_bffe1108632c64e4ef5525133e8ebcbc.jpg
    Giá: 15500000.0

  - Tên: Bóng golf
    Hình ảnh: https://admin.hi1.vn/uploads/bongGolfTitleist1_623b8db1028249390496a1010eda9e1a.jpg
    Giá: 1350000.0

  - Tên: Quần golf nam
    Hình ảnh: https://admin.hi1.vn/uploads/quanGolfNamHonma1_0864d62a45e32dc59ce0e63aab813915.jpg
    Giá: 6999000.0

  - Tên: Áo golf nữ
    Hình ảnh: https://admin.hi1.vn/uploads/aoGolfHazzyNu2_8ada718b42d00b8ef6b4d80aabc3e740.jpg
    Giá: 4099000.0
  ```
  ### <ins>**Lưu ý**</ins>:
  - Ở đây bot in ra câu trả lời dựa trên các trường dữ liệu dựa trên cài đặt có sẵn và bot chỉ được dạy để tập trung vào bảng productDetail, nếu bạn có thay đổi trong dữ liệu thì có thể sửa ngữ cảnh ở file **app/service/chatbot_data.py** tại biến **sql_prompt** dòng số 22:
    ```
    **Bạn CHỈ được phép sử dụng bảng sau:**
    - **public."productDetail":** Chứa thông tin chi tiết về sản phẩm. Các cột quan trọng: `id`, `name` (tên sản phẩm), `image` (dạng url chứa hình ảnh sản phẩm), `"paymentPrice"` (giá sản phẩm).
    ```
    Đây là phần giới hạn việc truy cập các bộ dữ liệu của bot, nó giúp tăng tốc khả năng xử lý của bot, bạn nên xoá nó nếu mong muốn lấy toàn bộ dữ liệu về.

    ```
    **Khi người dùng hỏi về sản phẩm, hãy làm theo các bước sau:**

    1.  **Tìm kiếm trực tiếp trong bảng `public."productDetail"`** cột `name` để tìm **sản phẩm phù hợp nhất** với câu hỏi của người dùng.
    2.  **Câu lệnh SQL có thể là:**
    - `SELECT id, name, image, "paymentPrice" FROM public."productDetail" WHERE name LIKE '%từ_khóa_sản_phẩm%';`
    **Chỉ trả về các cột `id`, `name`, `image` và `"paymentPrice"` từ bảng `public."productDetail"`.**
    ```
    Ở đây bạn xử lý lại yêu cầu tìm kiếm theo mong muốn cũng như sửa lại ví dụ câu lệnh SQL. Lưu ý rằng nếu dữ liệu của bạn được viết theo Camel Case (ví dụ như paymentPricing, outdoorAcitivity, userName) thì hãy để cụm biến trong dấu "", qua đó tránh việc bot hiểu nhầm paymentPrice thành paymentprice.