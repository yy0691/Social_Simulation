"""
测试增强的本地聊天系统
验证AI成员的真实、个性化发言机制
"""

import asyncio
import requests
import json
import time
from datetime import datetime

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
            print(f"   AI助手回复: {data['data'].get('ai_response', '无')}")
            print(f"   预计AI成员回复数: {data['data'].get('agent_responses_scheduled', 0)}")
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
        response = requests.get(f"{API_BASE}/api/v1/chat/messages?limit=15")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data["data"]["messages"]
        return []
            
    except Exception as e:
        print(f"❌ 获取消息失败: {str(e)}")
        return []

def display_recent_messages():
    """显示最近的聊天消息"""
    messages = get_messages()
    
    print("\n" + "="*80)
    print("📝 最近的聊天记录:")
    print("="*80)
    
    if not messages:
        print("暂无聊天记录")
        return
    
    for msg in messages[-10:]:  # 显示最近10条
        sender_icon = "🎮" if msg["isUser"] else "🤖" if msg["isAI"] else "👤" if msg["isAgent"] else "📢"
        timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")
        print(f"{sender_icon} {msg['sender']}: {msg['content']}")
    
    print("="*80)

def analyze_agent_responses():
    """分析AI成员回复的特点"""
    messages = get_messages()
    agent_messages = [msg for msg in messages if msg["isAgent"]]
    
    if not agent_messages:
        print("❌ 暂无AI成员回复")
        return
    
    print(f"\n🎭 AI成员回复分析 (共{len(agent_messages)}条):")
    print("-" * 60)
    
    # 统计每个成员的发言次数
    agent_counts = {}
    agent_styles = {}
    
    for msg in agent_messages:
        sender = msg["sender"]
        content = msg["content"]
        
        agent_counts[sender] = agent_counts.get(sender, 0) + 1
        
        if sender not in agent_styles:
            agent_styles[sender] = []
        agent_styles[sender].append(content)
    
    # 显示统计结果
    for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"👤 {agent}: {count}条发言")
        
        # 分析发言特点
        messages_by_agent = agent_styles[agent]
        avg_length = sum(len(msg) for msg in messages_by_agent) / len(messages_by_agent)
        
        # 检查是否有个性化特征
        has_greeting = any("我是" in msg for msg in messages_by_agent)
        has_personality = any(word in " ".join(messages_by_agent) for word in ["觉得", "认为", "想法", "经验", "角度"])
        has_questions = any("？" in msg or "吗" in msg for msg in messages_by_agent)
        
        features = []
        if has_greeting:
            features.append("自我介绍")
        if has_personality:
            features.append("个人观点")
        if has_questions:
            features.append("互动提问")
        if avg_length > 50:
            features.append("详细表达")
        elif avg_length < 30:
            features.append("简洁回复")
        
        print(f"   特征: {', '.join(features) if features else '基础回复'}")
        print(f"   平均长度: {avg_length:.1f}字")
        
        # 显示最新一条发言
        if messages_by_agent:
            latest = messages_by_agent[-1]
            print(f"   最新发言: {latest[:50]}{'...' if len(latest) > 50 else ''}")
        print()

def test_different_topics():
    """测试不同话题的AI成员参与度"""
    
    test_topics = [
        {
            "message": "大家好！今天天气真不错，适合出去走走！",
            "category": "日常问候",
            "expected": "外向型、乐观开朗的成员更活跃"
        },
        {
            "message": "我想组织一个读书分享会，大家觉得怎么样？",
            "category": "教育话题", 
            "expected": "教师、学生等教育相关成员更感兴趣"
        },
        {
            "message": "最近工作压力有点大，有什么放松的好方法吗？",
            "category": "健康话题",
            "expected": "医生、关心健康的成员会回复"
        },
        {
            "message": "有人对艺术感兴趣吗？我想办个画展",
            "category": "艺术话题",
            "expected": "艺术家、创造型成员会积极参与"
        },
        {
            "message": "我们社群的发展需要大家一起努力",
            "category": "社群建设",
            "expected": "领导型、关心社区的成员会发言"
        }
    ]
    
    print("\n🎯 测试不同话题的AI成员参与度")
    print("="*80)
    
    for i, topic in enumerate(test_topics, 1):
        print(f"\n📋 测试 {i}/{len(test_topics)}: {topic['category']}")
        print(f"💬 消息: {topic['message']}")
        print(f"🎯 预期: {topic['expected']}")
        
        # 记录发送前的消息数量
        before_messages = get_messages()
        before_count = len([msg for msg in before_messages if msg["isAgent"]])
        
        # 发送消息
        result = send_message(topic['message'])
        if not result:
            print("❌ 消息发送失败")
            continue
        
        # 等待AI成员回复
        print("⏰ 等待AI成员回复...")
        time.sleep(15)  # 等待15秒
        
        # 检查新的回复
        after_messages = get_messages()
        after_count = len([msg for msg in after_messages if msg["isAgent"]])
        new_responses = after_count - before_count
        
        print(f"📊 收到 {new_responses} 条新的AI成员回复")
        
        # 显示新回复
        if new_responses > 0:
            new_agent_messages = [msg for msg in after_messages if msg["isAgent"]][-new_responses:]
            for msg in new_agent_messages:
                print(f"   👤 {msg['sender']}: {msg['content'][:60]}{'...' if len(msg['content']) > 60 else ''}")
        
        print("-" * 60)
        
        # 间隔一下再发送下一条
        if i < len(test_topics):
            print("⏳ 等待5秒后发送下一条消息...")
            time.sleep(5)

def main():
    """主测试函数"""
    print("🚀 增强本地聊天系统测试开始")
    print("="*80)
    
    # 检查服务器连接
    try:
        response = requests.get(f"{API_BASE}/api/v1/chat/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ 服务器连接正常")
            print(f"📊 聊天系统状态: {status_data['data'].get('chat_system_status', '未知')}")
            print(f"📈 总消息数: {status_data['data'].get('total_messages', 0)}")
            print(f"👥 活跃AI成员: {status_data['data'].get('active_agent_count', 0)}")
        else:
            print(f"❌ 服务器连接失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接到服务器: {str(e)}")
        return
    
    # 显示当前聊天记录
    display_recent_messages()
    
    # 测试不同话题
    test_different_topics()
    
    # 最终分析
    print("\n🎭 最终AI成员回复分析:")
    analyze_agent_responses()
    
    print("\n🎉 测试完成！")
    print("\n💡 观察要点:")
    print("1. AI成员是否根据性格特征有不同的参与度？")
    print("2. 回复内容是否体现了个性和职业特点？")
    print("3. 回复时间是否有差异，不再是固定模式？")
    print("4. 对话是否更加自然，减少了机械化表达？")
    print("5. 不同话题是否吸引了不同类型的成员参与？")

if __name__ == "__main__":
    main() 