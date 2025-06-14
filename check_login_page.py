import requests

def check_login_page():
    try:
        response = requests.get('http://127.0.0.1:8000/login/')
        print("Status code:", response.status_code)
        print("\nPage content:")
        print(response.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_login_page()
