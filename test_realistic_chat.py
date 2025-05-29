"""
测试真实聊天系统
验证AI成员的自然发言机制
"""

import asyncio
import requests
import json
import time

API_BASE = "http://127.0.0.1:8000"

def send_message(message):
    """发送聊天消息"""
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/chat/send",
            json={"message": message},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 消息发送成功: {message}")
            return data
        else:
            print(f"❌ 发送失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 发送消息出错: {str(e)}")
        return None

def get_messages():
    """获取聊天消息"""
    try:
        response = requests.get(f"{API_BASE}/api/v1/chat/messages?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("messages", [])
        else:
            print(f"❌ 获取消息失败: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ 获取消息出错: {str(e)}")
        return []

def print_recent_messages():
    """打印最近的消息"""
    messages = get_messages()
    print("\n" + "="*60)
    print("📝 最近的聊天记录:")
    print("="*60)
    
    for msg in messages[-8:]:  # 显示最近8条消息
        sender = msg.get("sender", "未知")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")
        
        if msg.get("isUser"):
            print(f"🎮 玩家: {content}")
        elif msg.get("isAI"):
            print(f"🤖 AI助手: {content}")
        elif msg.get("isAgent"):
            print(f"👤 {sender}: {content}")
        else:
            print(f"📢 {sender}: {content}")
    
    print("="*60)

def test_realistic_chat():
    """测试真实聊天系统"""
    print("🧪 开始测试真实聊天系统...")
    
    # 测试用例
    test_messages = [
        "大家好！今天天气真不错",
        "我想组织一个读书分享会，大家觉得怎么样？",
        "最近工作压力有点大，有什么放松的好方法吗？",
        "我们社群的健康状况怎么样？需要改善什么吗？",
        "有人对艺术感兴趣吗？我想办个画展",
        "社群建设方面，大家有什么建议？"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🎯 测试 {i}/{len(test_messages)}: {message}")
        
        # 发送消息
        result = send_message(message)
        
        if result:
            print("⏰ 等待AI成员回复...")
            # 等待AI成员回复（给足够时间让所有成员回复）
            time.sleep(30)
            
            # 显示对话结果
            print_recent_messages()
            
            # 等待一段时间再发送下一条消息
            if i < len(test_messages):
                print("⏳ 等待5秒后发送下一条消息...")
                time.sleep(5)
        else:
            print("❌ 消息发送失败，跳过此测试")

def test_different_topics():
    """测试不同话题的AI成员参与度"""
    print("\n🎭 测试不同话题的AI成员参与度...")
    
    topic_tests = [
        {
            "message": "我们来讨论一下教育问题吧",
            "expected_participants": ["张明"],  # 教师应该更感兴趣
            "topic": "教育话题"
        },
        {
            "message": "最近身体不太舒服，有什么健康建议吗？",
            "expected_participants": ["王丽"],  # 医生应该更感兴趣
            "topic": "健康话题"
        },
        {
            "message": "我想学画画，有人能教我吗？",
            "expected_participants": ["李华"],  # 艺术家应该更感兴趣
            "topic": "艺术话题"
        },
        {
            "message": "社群的基础设施需要改善",
            "expected_participants": ["刘强"],  # 工程师应该更感兴趣
            "topic": "建设话题"
        }
    ]
    
    for test in topic_tests:
        print(f"\n🎯 测试{test['topic']}: {test['message']}")
        
        # 记录发送前的消息数量
        before_messages = get_messages()
        before_count = len(before_messages)
        
        # 发送消息
        send_message(test["message"])
        
        # 等待回复
        print("⏰ 等待AI成员回复...")
        time.sleep(25)
        
        # 检查回复
        after_messages = get_messages()
        new_messages = after_messages[before_count:]
        
        print(f"📊 收到 {len(new_messages)} 条新回复:")
        for msg in new_messages:
            if msg.get("isAgent"):
                sender = msg.get("sender")
                content = msg.get("content")
                print(f"  👤 {sender}: {content[:50]}...")
        
        time.sleep(3)

def test_personality_differences():
    """测试不同性格的AI成员回复差异"""
    print("\n🎭 测试AI成员性格差异...")
    
    # 发送一个中性话题，观察不同性格的回复
    message = "大家对未来有什么期待吗？"
    print(f"🎯 发送话题: {message}")
    
    before_messages = get_messages()
    before_count = len(before_messages)
    
    send_message(message)
    
    print("⏰ 等待各种性格的AI成员回复...")
    time.sleep(35)
    
    after_messages = get_messages()
    new_messages = after_messages[before_count:]
    
    print("📊 分析不同性格的回复特点:")
    for msg in new_messages:
        if msg.get("isAgent"):
            sender = msg.get("sender")
            content = msg.get("content")
            print(f"  👤 {sender}: {content}")
    
    print("\n💡 观察要点:")
    print("- 乐观开朗的成员回复是否积极正面")
    print("- 内向型成员是否回复较少或更深思熟虑")
    print("- 社交型成员是否更活跃")
    print("- 分析型成员是否更理性客观")

if __name__ == "__main__":
    print("🚀 真实聊天系统测试开始")
    print("="*60)
    
    try:
        # 基础功能测试
        test_realistic_chat()
        
        # 话题参与度测试
        test_different_topics()
        
        # 性格差异测试
        test_personality_differences()
        
        print("\n🎉 测试完成！")
        print("请观察AI成员的发言是否:")
        print("1. 不再机械化，更加自然")
        print("2. 根据性格和职业有不同的参与度")
        print("3. 回复时间不再固定，更加真实")
        print("4. 发言内容更有个性和深度")
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {str(e)}") 