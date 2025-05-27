 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    print("🚀 开始测试AI社群模拟小游戏API")
    print("=" * 50)
    
    # 测试1: 基础接口
    print("\n📋 测试基础接口:")
    try:
        r = requests.get(f"{base_url}/")
        print(f"✅ 根路径: {r.status_code}")
        print(f"   响应: {r.json()['message']}")
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
    
    try:
        r = requests.get(f"{base_url}/api/v1/health")
        print(f"✅ 健康检查: {r.status_code}")
        data = r.json()
        print(f"   服务: {data['service']}")
        print(f"   数据库: {data['components']['database']}")
    except Exception as e:
        print(f"❌ 健康检查测试失败: {e}")
    
    # 测试2: 社群接口
    print("\n🏘️ 测试社群接口:")
    try:
        r = requests.get(f"{base_url}/api/v1/community/status")
        print(f"✅ 社群状态: {r.status_code}")
        data = r.json()
        print(f"   人口: {data['population']}")
        print(f"   幸福度: {data['happiness']}")
        print(f"   活跃度: {data['activity']}")
        print(f"   资源: {data['resources']}")
    except Exception as e:
        print(f"❌ 社群状态测试失败: {e}")
    
    try:
        r = requests.get(f"{base_url}/api/v1/community/agents")
        print(f"✅ AI居民列表: {r.status_code}")
        data = r.json()
        print(f"   居民数量: {data['total_count']}")
        for agent in data['agents']:
            print(f"   - {agent['name']}: {agent['personality']} ({agent['role']})")
    except Exception as e:
        print(f"❌ AI居民列表测试失败: {e}")
    
    try:
        r = requests.get(f"{base_url}/api/v1/community/stats/summary")
        print(f"✅ 统计汇总: {r.status_code}")
        data = r.json()
        print(f"   总居民数: {data['totals']['agents']}")
        print(f"   总事件数: {data['totals']['events']}")
    except Exception as e:
        print(f"❌ 统计汇总测试失败: {e}")
    
    # 测试3: 指令执行
    print("\n🎮 测试指令执行:")
    try:
        # 执行积极指令
        payload = {
            "command": "组织社群聚会",
            "description": "让大家一起聚会庆祝"
        }
        r = requests.post(f"{base_url}/api/v1/commands/execute", json=payload)
        print(f"✅ 执行聚会指令: {r.status_code}")
        data = r.json()
        print(f"   影响类型: {data['impact_type']}")
        print(f"   幸福度变化: +{data['changes']['happiness']}")
        print(f"   活跃度变化: +{data['changes']['activity']}")
        print(f"   新幸福度: {data['new_stats']['happiness']}")
    except Exception as e:
        print(f"❌ 指令执行测试失败: {e}")
    
    # 测试4: 查看更新后的状态
    print("\n📊 指令执行后的状态:")
    try:
        r = requests.get(f"{base_url}/api/v1/community/status")
        print(f"✅ 更新后社群状态: {r.status_code}")
        data = r.json()
        print(f"   幸福度: {data['happiness']}")
        print(f"   活跃度: {data['activity']}")
    except Exception as e:
        print(f"❌ 更新后状态测试失败: {e}")
    
    # 测试5: 事件历史
    print("\n📝 测试事件历史:")
    try:
        r = requests.get(f"{base_url}/api/v1/community/events")
        print(f"✅ 事件历史: {r.status_code}")
        data = r.json()
        print(f"   事件数量: {len(data['events'])}")
        for event in data['events'][:3]:  # 显示前3个事件
            print(f"   - {event['type']}: {event['description']}")
    except Exception as e:
        print(f"❌ 事件历史测试失败: {e}")
    
    print("\n🎉 API测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_api()