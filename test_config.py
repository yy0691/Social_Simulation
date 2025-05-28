#!/usr/bin/env python3
"""
测试LLM配置是否正确读取
"""

import requests
import json
import time

def test_llm_config():
    """测试LLM配置"""
    print("🔍 测试LLM配置读取...")
    
    try:
        # 等待服务器启动
        time.sleep(2)
        
        # 调用API
        response = requests.get('http://127.0.0.1:8000/api/v1/system/llm/status')
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API调用成功!")
            print("=" * 50)
            print(f"配置有效: {data['data']['config_valid']}")
            print(f"配置消息: {data['data']['config_message']}")
            print(f"客户端初始化: {data['data']['client_initialized']}")
            print(f"提供商: {data['data']['provider']}")
            print(f"模型: {data['data']['model']}")
            print(f"最大Token: {data['data']['max_tokens']}")
            print(f"温度: {data['data']['temperature']}")
            print(f"超时: {data['data']['timeout']}")
            print("=" * 50)
            
            if data['data']['config_valid']:
                print("🎉 LLM配置有效!")
            else:
                print(f"❌ LLM配置问题: {data['data']['config_message']}")
            
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_full_llm_test():
    """运行完整的LLM测试"""
    print("\n🧪 运行完整LLM测试...")
    
    try:
        response = requests.post('http://127.0.0.1:8000/api/v1/system/llm/test')
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ 完整测试完成!")
            print("=" * 50)
            
            if data['success']:
                result = data['data']
                print(f"总体成功: {result['overall_success']}")
                print(f"配置检查: {result['config_check']}")
                print(f"客户端初始化: {result['client_init']}")
                print(f"API调用: {result['api_call']}")
                print(f"指令解析: {result['command_parse']}")
                print(f"AI响应: {result['agent_response']}")
                
                print("\n📝 详细日志:")
                for log in result['logs']:
                    print(f"  {log}")
                
                if result['errors']:
                    print("\n❌ 错误信息:")
                    for error in result['errors']:
                        print(f"  {error}")
            else:
                print(f"❌ 测试失败: {data['error']}")
        else:
            print(f"❌ 测试请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 完整测试失败: {str(e)}")

if __name__ == "__main__":
    test_llm_config()
    test_full_llm_test() 