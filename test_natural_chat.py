"""
测试自然聊天系统
验证AI成员是否能够自然地响应各种消息，而不是只围绕自己的专业说话
"""

import requests
import json
import time

def test_natural_chat():
    """测试自然聊天功能"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 测试自然聊天系统")
    print("=" * 60)
    
    # 测试用例 - 各种日常对话场景
    test_scenarios = [
        {
            "message": "大家好！新人报到，请多多关照～",
            "category": "新人问候",
            "expected": "应该有多个成员热情回应，而不是只有特定职业的人回复",
            "wait_time": 8
        },
        {
            "message": "今天心情不太好，有点郁闷...",
            "category": "情感分享",
            "expected": "应该有成员给予情感支持和安慰，不分职业",
            "wait_time": 10
        },
        {
            "message": "刚刚看了一部很棒的电影，推荐给大家！",
            "category": "生活分享",
            "expected": "各种职业的成员都可能感兴趣并参与讨论",
            "wait_time": 8
        },
        {
            "message": "我在考虑换个发型，大家觉得短发怎么样？",
            "category": "日常咨询",
            "expected": "不应该只有特定职业回应，普通的生活话题大家都会参与",
            "wait_time": 10
        },
        {
            "message": "谁知道附近哪里有好吃的火锅店？",
            "category": "实用询问",
            "expected": "本地生活话题，各行各业的人都可能知道",
            "wait_time": 8
        },
        {
            "message": "最近压力有点大，大家是怎么放松的呢？",
            "category": "经验咨询",
            "expected": "每个人都有自己的放松方式，不局限于特定职业",
            "wait_time": 10
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 场景 {i}: {scenario['category']}")
        print(f"消息: {scenario['message']}")
        print(f"期望: {scenario['expected']}")
        print("-" * 50)
        
        try:
            # 发送消息
            response = requests.post(
                f"{base_url}/chat/send",
                json={"message": scenario["message"]},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 消息发送成功")
                print(f"📊 预计AI成员回复数: {result['data']['agent_responses_scheduled']}")
                
                # 等待AI回复
                print(f"⏳ 等待{scenario['wait_time']}秒收集回复...")
                time.sleep(scenario['wait_time'])
                
                # 获取最新消息
                messages_response = requests.get(f"{base_url}/chat/messages?limit=15")
                if messages_response.status_code == 200:
                    messages_data = messages_response.json()
                    latest_messages = messages_data['data']['messages']
                    
                    # 分析AI成员回复
                    ai_responses = []
                    user_message_time = result['data']['timestamp']
                    
                    for msg in latest_messages:
                        if (msg['isAgent'] and 
                            msg['timestamp'] > user_message_time):
                            ai_responses.append(msg)
                    
                    if ai_responses:
                        print(f"🤖 收到 {len(ai_responses)} 个AI成员回复:")
                        
                        # 显示回复内容和分析
                        participants = set()
                        professional_responses = 0
                        natural_responses = 0
                        
                        for response_msg in ai_responses:
                            print(f"   👤 {response_msg['sender']}: {response_msg['content']}")
                            participants.add(response_msg['sender'])
                            
                            # 简单分析回复类型
                            content = response_msg['content'].lower()
                            if any(prof_word in content for prof_word in 
                                  ["从教学", "从医生", "从技术", "从商业", "作为老师", "作为医生"]):
                                professional_responses += 1
                            else:
                                natural_responses += 1
                        
                        # 分析结果
                        print(f"\n📈 回复分析:")
                        print(f"   • 参与成员: {', '.join(participants)} ({len(participants)}人)")
                        print(f"   • 专业化回复: {professional_responses}/{len(ai_responses)}")
                        print(f"   • 自然化回复: {natural_responses}/{len(ai_responses)}")
                        
                        # 检查是否过度专业化
                        if len(ai_responses) > 0:
                            professional_ratio = professional_responses / len(ai_responses)
                            if professional_ratio > 0.5:
                                print("   ⚠️ 专业化回复比例偏高，可能仍然过于依赖职业设定")
                            else:
                                print("   ✅ 自然化回复占主导，成员表现更像普通人")
                        
                        # 检查参与多样性
                        if len(participants) >= 2:
                            print("   ✅ 多成员参与，避免了固定成员发言")
                        else:
                            print("   ⚠️ 参与成员较少，可能需要调整参与度算法")
                            
                    else:
                        print("⚠️ 未收到AI成员回复")
                        
            else:
                print(f"❌ 发送失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 测试出错: {str(e)}")
        
        print("\n" + "="*60)
        if i < len(test_scenarios):
            print("等待3秒后进行下一个场景测试...")
            time.sleep(3)
    
    # 测试成员间互动
    test_member_interactions()

def test_member_interactions():
    """测试成员间的互动"""
    base_url = "http://localhost:8000/api/v1"
    
    print("\n🔄 测试成员间互动")
    print("=" * 40)
    
    interaction_tests = [
        {
            "message": "大家觉得现在的生活节奏是不是太快了？",
            "description": "测试成员是否会对其他成员的观点做出回应"
        },
        {
            "message": "我觉得周末应该多陪陪家人，工作再忙也要有生活。",
            "description": "测试成员是否会对具体观点表示同意或补充"
        }
    ]
    
    for test in interaction_tests:
        print(f"\n💬 互动测试: {test['description']}")
        print(f"消息: {test['message']}")
        
        try:
            response = requests.post(
                f"{base_url}/chat/send",
                json={"message": test["message"]},
                timeout=15
            )
            
            if response.status_code == 200:
                print("✅ 消息发送成功，等待12秒观察互动...")
                time.sleep(12)
                
                # 获取消息并分析互动
                messages_response = requests.get(f"{base_url}/chat/messages?limit=10")
                if messages_response.status_code == 200:
                    messages_data = messages_response.json()
                    latest_messages = messages_data['data']['messages']
                    
                    print("📝 最近的对话:")
                    interaction_count = 0
                    for msg in latest_messages[-6:]:  # 显示最近6条
                        sender_type = "👤" if msg['isAgent'] else "🧑" if msg['isUser'] else "🤖"
                        print(f"   {sender_type} {msg['sender']}: {msg['content']}")
                        
                        # 检查是否有互动标志
                        if msg['isAgent'] and ("@" in msg['content'] or "同意" in msg['content'] or "觉得" in msg['content']):
                            interaction_count += 1
                    
                    if interaction_count > 0:
                        print(f"✅ 检测到 {interaction_count} 次成员间互动")
                    else:
                        print("ℹ️ 暂未检测到明显的成员间互动")
                        
        except Exception as e:
            print(f"❌ 互动测试失败: {str(e)}")
        
        time.sleep(3)

def main():
    print("🚀 开始自然聊天系统测试")
    print("请确保后端服务正在运行 (localhost:8000)")
    input("按回车键开始测试...")
    
    test_natural_chat()
    
    print("\n🎉 测试完成！")
    print("\n💡 评估标准:")
    print("   ✅ 好的表现:")
    print("      - 多成员参与各种话题")
    print("      - 自然化回复多于专业化回复")
    print("      - 成员对他人发言有回应")
    print("      - 回复内容贴近普通人的日常对话")
    print("   ⚠️ 需要改进:")
    print("      - 过度依赖职业设定")
    print("      - 只有特定成员总是发言")
    print("      - 缺乏成员间互动")
    print("      - 回复过于机械化或专业化")

if __name__ == "__main__":
    main() 