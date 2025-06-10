import requests
import json

# 伙伴云API配置
API_BASE_URL = "https://api.huoban.com/openapi/v1"
API_KEY = "wPCoGnaYtQrNXoWv3I0VOrKnYQpOU8XNSyr5OzuJ"  # 您的API密钥
SPACE_ID = "4000000007763686"  # 您的空间ID

# 表格ID
UNIVERSITY_TABLES = {
    "private": "2100000065741189", 
    "public_graduate": "2100000065744137",
    "public_undergrad": "2100000065744831"
}

def _headers():
    """返回标准API请求头"""
    return {
        "Open-Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

def test_api_endpoints():
    """测试多个可能的API端点"""
    print("===== 伙伴云API基础测试 =====\n")
    
    # 测试端点1: 表格列表
    test_endpoint("table/list", {"space_id": SPACE_ID})
    
    # 测试端点2: 单个表格信息
    test_endpoint("table", {"table_id": UNIVERSITY_TABLES["private"]})
    
    # 测试端点3: 表格数据查询
    test_endpoint("item/list", {"table_id": UNIVERSITY_TABLES["private"], "limit": 5})
    
    # 测试端点4: 空间信息 (可能的端点)
    test_endpoint("space", {"space_id": SPACE_ID})
    
    # 可以继续添加其他可能的端点测试...
    
    print("\n===== 测试完成 =====")

def test_endpoint(endpoint, payload):
    """测试单个API端点"""
    url = f"{API_BASE_URL}/{endpoint}"
    print(f"\n正在测试: {url}")
    print(f"请求数据: {json.dumps(payload)}")
    
    try:
        response = requests.post(url, headers=_headers(), json=payload)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print(f"✓ 成功! 返回数据示例: {json.dumps(data)[:200]}..." if len(json.dumps(data)) > 200 else json.dumps(data))
            else:
                print(f"✗ API返回错误: {data.get('message', '未知错误')}")
        else:
            print(f"✗ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")

def test_single_table_items(table_id):
    """详细测试单个表格的数据获取"""
    print(f"\n===== 测试表格 {table_id} 数据获取 =====")
    url = f"{API_BASE_URL}/item/list"
    payload = {
        "table_id": table_id,
        "limit": 3
    }
    
    try:
        response = requests.post(url, headers=_headers(), json=payload)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                items = data.get("data", {}).get("items", [])
                print(f"✓ 成功获取表格数据，共 {len(items)} 条")
                
                # 显示每条数据的基本信息
                for i, item in enumerate(items):
                    item_id = item.get("item_id", "无ID")
                    fields = item.get("fields", {})
                    print(f"\n数据项 {i+1}:")
                    print(f"  ID: {item_id}")
                    print(f"  字段数量: {len(fields)}")
                    
                    # 尝试显示前几个字段
                    for j, (field_id, value) in enumerate(fields.items()):
                        if j >= 3: # 只显示前3个字段
                            print(f"  ... 等 {len(fields) - 3} 个字段")
                            break
                        print(f"  {field_id}: {value}")
            else:
                print(f"✗ API返回错误: {data.get('message', '未知错误')}")
        else:
            print(f"✗ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")

if __name__ == "__main__":
    # 先测试多个基本端点
    test_api_endpoints()
    
    # 然后详细测试一个表格的数据
    test_single_table_items(UNIVERSITY_TABLES["private"])