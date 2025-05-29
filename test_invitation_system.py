#!/usr/bin/env python3
"""
邀请系统功能测试脚本
测试社群成员邀请朋友的各项功能
"""

import asyncio
import requests
import json
import time
from datetime import datetime, timedelta

# API基础地址
BASE_URL = "http://localhost:8000"

class InvitationSystemTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
    
    def test_api_connection(self):
        """测试API连接"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health")
            if response.status_code == 200:
                print("✅ API连接正常")
                return True
            else:
                print(f"❌ API连接失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API连接异常: {str(e)}")
            return False
    
    def get_active_agents(self):
        """获取活跃的居民列表"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/community/agents")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    agents = [agent for agent in data["data"] if agent.get("is_active")]
                    print(f"✅ 获取到 {len(agents)} 个活跃居民")
                    return agents
                else:
                    print("❌ 获取居民列表失败")
                    return []
            else:
                print(f"❌ 获取居民列表请求失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取居民列表异常: {str(e)}")
            return []
    
    def test_send_invitation(self, agent_name):
        """测试发送邀请"""
        invitation_data = {
            "inviter_agent_name": agent_name,
            "invitee_email": f"test_friend_{int(time.time())}@example.com",
            "invitee_name": f"测试朋友_{int(time.time())}",
            "invitation_message": f"这是来自 {agent_name} 的测试邀请！欢迎加入我们的AI社群！"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/invitation/send",
                json=invitation_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    invitation_code = data["data"]["invitation_code"]
                    print(f"✅ {agent_name} 成功发送邀请，邀请码: {invitation_code}")
                    return invitation_code
                else:
                    print(f"❌ 发送邀请失败: {data.get('message', '未知错误')}")
                    return None
            else:
                print(f"❌ 发送邀请请求失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 发送邀请异常: {str(e)}")
            return None
    
    def test_check_invitation(self, invitation_code):
        """测试检查邀请状态"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/invitation/check/{invitation_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    invitation_info = data["data"]
                    print(f"✅ 邀请信息查询成功:")
                    print(f"   邀请者: {invitation_info['inviter_name']}")
                    print(f"   被邀请者: {invitation_info['invitee_name']}")
                    print(f"   状态: {invitation_info['status']}")
                    print(f"   邀请消息: {invitation_info['invitation_message']}")
                    return invitation_info
                else:
                    print(f"❌ 查询邀请信息失败: {data.get('message', '未知错误')}")
                    return None
            else:
                print(f"❌ 查询邀请请求失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 查询邀请异常: {str(e)}")
            return None
    
    def test_respond_invitation(self, invitation_code, response_type="accept"):
        """测试回应邀请"""
        response_data = {
            "invitation_code": invitation_code,
            "response": response_type,
            "response_message": f"测试{response_type}邀请回应"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/invitation/respond",
                json=response_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ 邀请回应成功: {data['message']}")
                    return True
                else:
                    print(f"❌ 邀请回应失败: {data.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ 邀请回应请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 邀请回应异常: {str(e)}")
            return False
    
    def test_get_invitations(self):
        """测试获取邀请列表"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/invitation/list")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    invitations = data["data"]["invitations"]
                    print(f"✅ 获取邀请列表成功，共 {len(invitations)} 个邀请")
                    for invitation in invitations[:3]:  # 只显示前3个
                        print(f"   {invitation['inviter_name']} -> {invitation['invitee_name']} ({invitation['status']})")
                    return invitations
                else:
                    print(f"❌ 获取邀请列表失败: {data.get('message', '未知错误')}")
                    return []
            else:
                print(f"❌ 获取邀请列表请求失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取邀请列表异常: {str(e)}")
            return []
    
    def test_create_friendship(self, agent1_name, agent2_name):
        """测试创建好友关系"""
        friendship_data = {
            "agent_name_1": agent1_name,
            "agent_name_2": agent2_name
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/invitation/friendship/create",
                json=friendship_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ 好友关系创建成功: {data['message']}")
                    return True
                else:
                    print(f"❌ 好友关系创建失败: {data.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ 好友关系创建请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 好友关系创建异常: {str(e)}")
            return False
    
    def test_get_friendships(self):
        """测试获取好友关系列表"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/invitation/friendships")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    friendships = data["data"]["friendships"]
                    print(f"✅ 获取好友关系列表成功，共 {len(friendships)} 个好友关系")
                    for friendship in friendships[:3]:  # 只显示前3个
                        print(f"   {friendship['agent_name_1']} <-> {friendship['agent_name_2']} (友谊等级: {friendship['friendship_level']})")
                    return friendships
                else:
                    print(f"❌ 获取好友关系列表失败: {data.get('message', '未知错误')}")
                    return []
            else:
                print(f"❌ 获取好友关系列表请求失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取好友关系列表异常: {str(e)}")
            return []
    
    def test_get_members(self):
        """测试获取社群成员列表"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/invitation/members")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    members = data["data"]["members"]
                    print(f"✅ 获取社群成员列表成功，共 {len(members)} 个成员")
                    for member in members[:5]:  # 只显示前5个
                        print(f"   {member['member_name']} ({member['member_type']}) - {member['join_method']}")
                    return members
                else:
                    print(f"❌ 获取社群成员列表失败: {data.get('message', '未知错误')}")
                    return []
            else:
                print(f"❌ 获取社群成员列表请求失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取社群成员列表异常: {str(e)}")
            return []
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 开始邀请系统综合测试...")
        print("=" * 60)
        
        # 1. 测试API连接
        print("\n1. 测试API连接")
        if not self.test_api_connection():
            print("API连接失败，终止测试")
            return
        
        # 2. 获取活跃居民
        print("\n2. 获取活跃居民")
        agents = self.get_active_agents()
        if len(agents) < 2:
            print("活跃居民不足，无法进行完整测试")
            return
        
        # 3. 测试发送邀请
        print("\n3. 测试发送邀请")
        test_agent = agents[0]
        invitation_code = self.test_send_invitation(test_agent["name"])
        
        if invitation_code:
            # 4. 测试检查邀请状态
            print("\n4. 测试检查邀请状态")
            self.test_check_invitation(invitation_code)
            
            # 5. 测试回应邀请（接受）
            print("\n5. 测试回应邀请（接受）")
            self.test_respond_invitation(invitation_code, "accept")
        
        # 6. 测试获取邀请列表
        print("\n6. 测试获取邀请列表")
        self.test_get_invitations()
        
        # 7. 测试创建好友关系
        print("\n7. 测试创建好友关系")
        if len(agents) >= 2:
            self.test_create_friendship(agents[0]["name"], agents[1]["name"])
        
        # 8. 测试获取好友关系列表
        print("\n8. 测试获取好友关系列表")
        self.test_get_friendships()
        
        # 9. 测试获取社群成员列表
        print("\n9. 测试获取社群成员列表")
        self.test_get_members()
        
        print("\n" + "=" * 60)
        print("✅ 邀请系统综合测试完成！")

def main():
    """主函数"""
    tester = InvitationSystemTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 