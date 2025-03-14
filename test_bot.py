import requests
import json

def interact_with_chatbot(query):
    try:
        url = "http://localhost:8000/chatbot/ask"

        headers = {'Content-Type': 'application/json'}

        # Tạo payload (data gửi vào request)
        payload = json.dumps({"query": query})
        # Gửi POST request
        response = requests.post(url, headers=headers, data=payload)

        # Kiểm tra yêu cầu có thành công hay không
        if response.status_code == 200:
            response_data = response.json()
            return response_data["response"]
        else:
            return f"Error: Yêu cầu thất bại với lỗi {response.status_code} - {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Error: Không thể kết nối đến API. {e}"
    except json.JSONDecodeError:
        return "Error: JSON trả về không hợp lệ từ API."
    except KeyError:
        return "Error: JSON trả về thiếu khoá 'response'."

def test_chatbot_query(query):
    response = interact_with_chatbot(query)
    print(f"\nBot: {response}\n")

if __name__ == '__main__':
    print("Nhập 'exit' để thoát")
    while True:
        query = input("Bạn: ")
        if query.lower() == 'exit':
            break  # Thoát vòng lặp khi người dùng nhập 'exit'
        test_chatbot_query(query)