"""
测试参与性聊天系统
验证AI成员是否能够给出具体参与性回复而非空洞评价性回复
"""

import requests
import json
import time

def test_participatory_responses():
    """测试参与性回复功能"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🎯 测试参与性回复系统")
    print("=" * 60)
    print("目标：AI成员应该给出具体的行为、经验和建议，而不是空洞的评价")
    print()
    
    # 核心测试场景 - 专门测试用户提到的问题
    test_scenarios = [
        {
            "message": "最近压力有点大，大家是怎么放松的呢？",
            "category": "放松方式询问",
            "expected_bad": ["这个观点很棒", "讨论氛围", "学到了很多"],
            "expected_good": ["我通常会", "我喜欢去", "我经常", "我会做"],
            "description": "应该回答具体的放松方式，如'我通常会去跑步'而不是'这个观点很棒'"
        },
        {
            "message": "工作遇到困难，大家有什么建议吗？",
            "category": "经验咨询",
            "expected_bad": ["很有启发", "值得思考", "讨论很有价值"],
            "expected_good": ["我之前遇到过", "我建议你可以", "我的经验是", "你可以试试"],
            "description": "应该给出具体建议和经验，而不是评价性回复"
        },
        {
            "message": "周末想去哪里玩，有推荐的地方吗？",
            "category": "地点推荐",
            "expected_bad": ["这个想法很好", "很有意思", "值得深入"],
            "expected_good": ["我知道", "我推荐", "我经常去", "有个地方"],
            "description": "应该推荐具体地点，而不是评价问题本身"
        },
        {
            "message": "学习新技能有什么好方法？",
            "category": "方法询问",
            "expected_bad": ["观点新颖", "很有道理", "学到新东西"],
            "expected_good": ["我通常", "我发现", "我建议", "你可以"],
            "description": "应该分享具体的学习方法和经验"
        },
        {
            "message": "想换个发型，短发怎么样？",
            "category": "个人选择",
            "expected_bad": ["这个话题有意思", "值得考虑", "很有启发"],
            "expected_good": ["我觉得短发", "我之前也", "我建议", "我朋友"],
            "description": "应该给出具体的建议和个人经验"
        },
        {
            "message": "附近哪里有好吃的火锅店？",
            "category": "具体询问",
            "expected_bad": ["这个问题很实用", "大家的建议", "讨论很有用"],
            "expected_good": ["我知道", "XX路上有", "我经常去", "我推荐"],
            "description": "应该推荐具体的店铺位置"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"📝 场景 {i}: {scenario['category']}")
        print(f"消息: {scenario['message']}")
        print(f"期望: {scenario['description']}")
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
                
                # 等待AI回复
                wait_time = 12
                print(f"⏳ 等待{wait_time}秒收集回复...")
                time.sleep(wait_time)
                
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
                        
                        # 分析回复质量
                        participatory_count = 0
                        evaluative_count = 0
                        total_responses = len(ai_responses)
                        
                        response_analysis = []
                        
                        for response_msg in ai_responses:
                            content = response_msg['content']
                            sender = response_msg['sender']
                            print(f"   👤 {sender}: {content}")
                            
                            # 检查是否包含评价性语言（坏的）
                            is_evaluative = any(bad_phrase in content for bad_phrase in scenario['expected_bad'])
                            
                            # 检查是否包含参与性语言（好的）
                            is_participatory = any(good_phrase in content for good_phrase in scenario['expected_good'])
                            
                            if is_evaluative:
                                evaluative_count += 1
                                response_type = "❌ 评价性"
                            elif is_participatory:
                                participatory_count += 1
                                response_type = "✅ 参与性"
                            else:
                                # 进一步分析
                                if any(word in content for word in ["我", "我会", "我觉得", "我建议", "我知道", "我经常", "我喜欢"]):
                                    participatory_count += 1
                                    response_type = "✅ 参与性(个人经验)"
                                else:
                                    response_type = "⚠️ 中性"
                            
                            response_analysis.append({
                                "sender": sender,
                                "content": content,
                                "type": response_type
                            })
                        
                        # 计算比例
                        if total_responses > 0:
                            participatory_ratio = participatory_count / total_responses
                            evaluative_ratio = evaluative_count / total_responses
                            
                            print(f"\n📊 回复质量分析:")
                            print(f"   • 参与性回复: {participatory_count}/{total_responses} ({participatory_ratio:.1%})")
                            print(f"   • 评价性回复: {evaluative_count}/{total_responses} ({evaluative_ratio:.1%})")
                            
                            # 评估结果
                            if participatory_ratio >= 0.8:
                                quality_score = "🌟 优秀"
                            elif participatory_ratio >= 0.6:
                                quality_score = "✅ 良好"
                            elif participatory_ratio >= 0.4:
                                quality_score = "⚠️ 一般"
                            else:
                                quality_score = "❌ 需改进"
                            
                            print(f"   • 总体质量: {quality_score}")
                            
                            # 记录结果
                            results.append({
                                "scenario": scenario['category'],
                                "total_responses": total_responses,
                                "participatory_ratio": participatory_ratio,
                                "evaluative_ratio": evaluative_ratio,
                                "quality_score": quality_score,
                                "details": response_analysis
                            })
                        
                    else:
                        print("⚠️ 未收到AI成员回复")
                        results.append({
                            "scenario": scenario['category'],
                            "total_responses": 0,
                            "participatory_ratio": 0,
                            "evaluative_ratio": 0,
                            "quality_score": "❌ 无回复"
                        })
                        
            else:
                print(f"❌ 发送失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 测试出错: {str(e)}")
        
        print("\n" + "="*60)
        if i < len(test_scenarios):
            print("等待3秒后进行下一个场景测试...")
            time.sleep(3)
    
    # 生成总结报告
    generate_summary_report(results)

def generate_summary_report(results):
    """生成测试总结报告"""
    print("\n🎉 参与性回复测试完成！")
    print("=" * 60)
    
    if not results:
        print("❌ 没有收集到测试结果")
        return
    
    # 计算总体指标
    total_scenarios = len(results)
    total_responses = sum(r['total_responses'] for r in results)
    avg_participatory = sum(r['participatory_ratio'] for r in results if r['total_responses'] > 0) / max(1, len([r for r in results if r['total_responses'] > 0]))
    avg_evaluative = sum(r['evaluative_ratio'] for r in results if r['total_responses'] > 0) / max(1, len([r for r in results if r['total_responses'] > 0]))
    
    print(f"📈 总体测试结果:")
    print(f"   • 测试场景数: {total_scenarios}")
    print(f"   • 总回复数: {total_responses}")
    print(f"   • 平均参与性比例: {avg_participatory:.1%}")
    print(f"   • 平均评价性比例: {avg_evaluative:.1%}")
    
    # 分场景结果
    print(f"\n📋 分场景结果:")
    for result in results:
        print(f"   • {result['scenario']}: {result['quality_score']} (参与性 {result['participatory_ratio']:.1%})")
    
    # 最佳和最差表现
    if results:
        best_result = max(results, key=lambda x: x['participatory_ratio'])
        worst_result = min(results, key=lambda x: x['participatory_ratio'])
        
        print(f"\n🌟 最佳表现: {best_result['scenario']} (参与性 {best_result['participatory_ratio']:.1%})")
        print(f"⚠️ 最差表现: {worst_result['scenario']} (参与性 {worst_result['participatory_ratio']:.1%})")
    
    # 改进建议
    print(f"\n💡 评估标准:")
    print(f"   ✅ 参与性回复 (好):")
    print(f"      - 具体行为: '我通常会去跑步'")
    print(f"      - 个人经验: '我之前遇到过类似情况'")
    print(f"      - 具体建议: '我建议你可以试试XX'")
    print(f"      - 实际推荐: '我知道XX路上有家店很不错'")
    
    print(f"\n   ❌ 评价性回复 (差):")
    print(f"      - 空洞评价: '这个观点很棒'")
    print(f"      - 讨论元评价: '讨论氛围很好'")
    print(f"      - 学习表态: '学到了很多新东西'")
    print(f"      - 泛泛而谈: '值得深入思考'")
    
    if avg_participatory >= 0.8:
        print(f"\n🎉 系统表现: 优秀！AI成员能够提供具体、实用的参与性回复")
    elif avg_participatory >= 0.6:
        print(f"\n✅ 系统表现: 良好，大部分回复具有参与性")
    elif avg_participatory >= 0.4:
        print(f"\n⚠️ 系统表现: 一般，需要进一步优化参与性回复比例")
    else:
        print(f"\n❌ 系统表现: 需要改进，评价性回复过多，缺乏具体内容")

def main():
    print("🚀 参与性vs评价性回复测试")
    print("测试目标：验证AI成员是否能给出具体的行为和经验，而非空洞评价")
    print("请确保后端服务正在运行 (localhost:8000)")
    input("按回车键开始测试...")
    
    test_participatory_responses()

if __name__ == "__main__":
    main() 