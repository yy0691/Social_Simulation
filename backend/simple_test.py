import requests; r = requests.get("http://127.0.0.1:8000/"); print("状态码:", r.status_code); print("响应:", r.text)
