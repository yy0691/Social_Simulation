"""
测试优化的AI聊天系统
验证基于六大提示词核心模块的真实对话效果
"""

import requests
import json
import time
import asyncio

def test_chat_api():
    """测试聊天API"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 测试优化的AI聊天系统")
    print("=" * 50)
    
    # 测试用例 - 不同话题的消息
    test_messages = [
        {
            "message": "大家好！最近有什么有趣的事情想分享吗？",
            "category": "社交互动",
            "description": "测试社交话题的参与度和回复质量"
        },
        {
            "message": "我最近在学习新的编程技术，有没有人一起交流学习心得？",
            "category": "教育学习",
            "description": "测试教育话题的专业性回复"
        },
        {
            "message": "天气这么好，大家有什么健康的运动建议吗？",
            "category": "健康生活",
            "description": "测试健康话题的专业建议"
        },
        {
            "message": "我在考虑创业，想听听大家对商业模式的看法。",
            "category": "商业讨论",
            "description": "测试商业话题的专业视角"
        },
        {
            "message": "最近看了一部很棒的电影，想和大家聊聊艺术和创意。",
            "category": "艺术文化",
            "description": "测试艺术话题的创意表达"
        }
    ]
    
    for i, test_case in enumerate(test_messages, 1):
        print(f"\n📝 测试案例 {i}: {test_case['category']}")
        print(f"描述: {test_case['description']}")
        print(f"消息: {test_case['message']}")
        print("-" * 40)
        
        try:
            # 发送消息
            response = requests.post(
                f"{base_url}/chat/send",
                json={"message": test_case["message"]},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 消息发送成功")
                print(f"📊 预计AI成员回复数: {result['data']['agent_responses_scheduled']}")
                
                # 等待AI回复
                print("⏳ 等待AI成员回复...")
                time.sleep(12)  # 等待回复生成
                
                # 获取最新消息
                messages_response = requests.get(f"{base_url}/chat/messages?limit=10")
                if messages_response.status_code == 200:
                    messages_data = messages_response.json()
                    latest_messages = messages_data['data']['messages']
                    
                    # 显示AI成员回复
                    ai_responses = []
                    for msg in latest_messages:
                        if msg['isAgent'] and msg['timestamp'] > result['data']['timestamp']:
                            ai_responses.append(msg)
                    
                    if ai_responses:
                        print(f"🤖 收到 {len(ai_responses)} 个AI成员回复:")
                        for response_msg in ai_responses:
                            print(f"   👤 {response_msg['sender']}: {response_msg['content']}")
                            
                        # 分析回复质量
                        analyze_response_quality(ai_responses, test_case)
                    else:
                        print("⚠️ 未收到AI成员回复")
                
            else:
                print(f"❌ 发送失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 测试出错: {str(e)}")
        
        print("\n" + "="*50)
        if i < len(test_messages):
            print("等待5秒后进行下一个测试...")
            time.sleep(5)
    
    # 测试完成后检查系统状态
    print("\n📊 检查聊天系统状态")
    check_system_status()

def analyze_response_quality(responses, test_case):
    """分析回复质量"""
    print("\n📈 回复质量分析:")
    
    # 检查回复多样性
    unique_senders = set(msg['sender'] for msg in responses)
    print(f"   • 参与成员数: {len(unique_senders)}")
    print(f"   • 参与成员: {', '.join(unique_senders)}")
    
    # 检查回复长度和质量
    avg_length = sum(len(msg['content']) for msg in responses) / len(responses)
    print(f"   • 平均回复长度: {avg_length:.1f} 字符")
    
    # 检查是否有重复内容
    contents = [msg['content'] for msg in responses]
    unique_contents = set(contents)
    if len(unique_contents) == len(contents):
        print("   • ✅ 回复内容无重复")
    else:
        print("   • ⚠️ 发现重复回复内容")
    
    # 检查专业性（简单关键词检测）
    category_keywords = {
        "教育学习": ["学习", "教育", "知识", "经验", "分享"],
        "健康生活": ["健康", "运动", "身体", "锻炼", "建议"],
        "商业讨论": ["商业", "创业", "市场", "经验", "建议"],
        "艺术文化": ["艺术", "创意", "文化", "美", "感受"]
    }
    
    if test_case['category'] in category_keywords:
        keywords = category_keywords[test_case['category']]
        professional_responses = 0
        for msg in responses:
            if any(keyword in msg['content'] for keyword in keywords):
                professional_responses += 1
        
        professional_ratio = professional_responses / len(responses)
        print(f"   • 专业相关性: {professional_ratio:.1%} ({professional_responses}/{len(responses)})")

def check_system_status():
    """检查系统状态"""
    try:
        response = requests.get("http://localhost:8000/api/v1/chat/status")
        if response.status_code == 200:
            status = response.json()['data']
            print(f"   • 聊天系统状态: {status['chat_system_status']}")
            print(f"   • 总消息数: {status['total_messages']}")
            print(f"   • AI成员消息数: {status['agent_messages']}")
            print(f"   • 活跃成员数: {status['active_agent_count']}")
            if status['active_agents']:
                print(f"   • 活跃成员: {', '.join(status['active_agents'])}")
        else:
            print("❌ 无法获取系统状态")
    except Exception as e:
        print(f"❌ 状态检查失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 开始测试优化的AI聊天系统")
    print("请确保后端服务正在运行 (localhost:8000)")
    input("按回车键开始测试...")
    
    test_chat_api()
    
    print("\n🎉 测试完成！")
    print("💡 优化要点:")
    print("   1. 基于六大提示词核心模块设计")
    print("   2. 角色设定更加详细和一致")
    print("   3. 专业知识库驱动的回复")
    print("   4. 避免重复和机械化表达")
    print("   5. 智能参与度控制") 