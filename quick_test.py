import requests; r = requests.get("http://127.0.0.1:8000/api/v1/community/status"); print("状态码:", r.status_code); print("响应内容:", r.text[:200])
