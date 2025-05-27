import requests
r = requests.get('http://127.0.0.1:8000/api/v1/community/status')
print('Status Code:', r.status_code)
print('Response:', r.text)
