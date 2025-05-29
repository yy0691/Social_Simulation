import requests
import json

def test_chat_api():
    """简单测试聊天API"""
    url = "http://localhost:8000/api/v1/chat/send"
    data = {"message": "测试消息"}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ API调用成功")
        else:
            print("❌ API调用失败")
            
    except Exception as e:
        print(f"❌ 请求出错: {str(e)}")

if __name__ == "__main__":
    test_chat_api() 