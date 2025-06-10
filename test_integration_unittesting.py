import unittest
import requests
import json
import time

# 伙伴云API配置
API_BASE_URL = "https://api.huoban.com/openapi/v1"
API_KEY = "wPCoGnaYtQrNXoWv3I0VOrKnYQpOU8XNSyr5OzuJ"
SPACE_ID = "4000000007763686"

# 大学表格配置
UNIVERSITY_TABLES = {
    "private": "2100000065741189",
    "public_graduate": "2100000065744137",
    "public_undergrad": "2100000065744831"
}

class HuobanyunAPITest(unittest.TestCase):
    """伙伴云API测试类"""
    
    def setUp(self):
        """测试前准备工作"""
        self.headers = {
            "Open-Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    
    def test_01_table_list(self):
        """测试获取表格列表"""
        print("\n测试获取表格列表...")
        url = f"{API_BASE_URL}/table/list"
        payload = {"space_id": SPACE_ID}
        
        response = requests.post(url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200, f"表格列表请求失败: {response.text}")
        
        data = response.json()
        self.assertEqual(data.get("code"), 0, f"业务逻辑错误: {data.get('message')}")
        
        tables = data.get("data", {}).get("tables", [])
        self.assertGreater(len(tables), 0, "表格列表为空")
        
        print(f"✓ 成功获取表格列表，共 {len(tables)} 个表格")
        return tables
    
    def test_02_university_tables_exist(self):
        """测试验证大学表格是否存在"""
        print("\n测试验证大学表格是否存在...")
        tables = self.test_01_table_list()
        
        # 获取所有表格ID
        table_ids = [table.get("table_id") for table in tables]
        
        # 验证每个大学表格ID是否存在
        for table_type, table_id in UNIVERSITY_TABLES.items():
            self.assertIn(table_id, table_ids, f"{table_type}表格ID在系统中不存在")
            print(f"✓ {table_type}表格ID存在")
    
    def test_03_get_items_from_each_university_table(self):
        """测试从每个大学表格获取数据"""
        print("\n测试从每个大学表格获取数据...")
        
        for table_type, table_id in UNIVERSITY_TABLES.items():
            print(f"\n获取{table_type}表格数据...")
            url = f"{API_BASE_URL}/item/list"
            payload = {"table_id": table_id, "limit": 5}
            
            response = requests.post(url, headers=self.headers, json=payload)
            self.assertEqual(response.status_code, 200, f"{table_type}表格数据请求失败: {response.text}")
            
            data = response.json()
            self.assertEqual(data.get("code"), 0, f"业务逻辑错误: {data.get('message')}")
            
            items = data.get("data", {}).get("items", [])
            print(f"✓ 成功获取{table_type}表格数据，共 {len(items)} 条")
            
            # 打印第一条数据的部分字段作为示例
            if items:
                print(f"  示例数据(ID: {items[0].get('item_id')}):")
                fields = items[0].get("fields", {})
                for i, (field_id, value) in enumerate(fields.items()):
                    if i >= 3:  # 只显示前3个字段
                        break
                    print(f"  - {field_id}: {value}")
    
    def test_04_alternative_table_endpoint(self):
        """测试可能的替代表格详情端点"""
        print("\n测试可能的替代表格详情端点...")
        
        # 尝试几种可能的表格详情端点
        endpoints = [
            "table/get",
            "table/detail",
            "table/info"
        ]
        
        table_id = UNIVERSITY_TABLES["private"]
        success = False
        
        for endpoint in endpoints:
            url = f"{API_BASE_URL}/{endpoint}"
            payload = {"table_id": table_id}
            
            print(f"尝试: {url}")
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    print(f"✓ 成功! 表格详情端点: {endpoint}")
                    success = True
                    break
            
            print(f"✗ 端点 {endpoint} 失败: {response.status_code}")
        
        # 这只是信息性测试，不断言结果
        if not success:
            print("⚠ 未找到可用的表格详情端点，但不会影响主要功能测试")

    def test_05_check_field_structure(self):
        """检查字段结构以便于映射"""
        print("\n检查字段结构...")
        
        # 选择一个表格进行字段结构分析
        table_id = UNIVERSITY_TABLES["private"]
        url = f"{API_BASE_URL}/item/list"
        payload = {
            "table_id": table_id,
            "limit": 1,
            "with_field_config": 1  # 请求包含字段配置信息
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200, f"字段结构请求失败: {response.text}")
        
        data = response.json()
        self.assertEqual(data.get("code"), 0, f"业务逻辑错误: {data.get('message')}")
        
        # 尝试获取字段配置
        fields_config = data.get("data", {}).get("fields", [])
        if fields_config:
            print(f"✓ 成功获取字段配置，共 {len(fields_config)} 个字段")
            for i, field in enumerate(fields_config[:3]):  # 只显示前3个字段
                print(f"  - {field.get('field_id')}: {field.get('name')}")
            if len(fields_config) > 3:
                print(f"  ... 等 {len(fields_config) - 3} 个字段")
        else:
            # 如果没有直接返回字段配置，尝试从数据项分析字段
            items = data.get("data", {}).get("items", [])
            if items:
                fields = items[0].get("fields", {})
                print(f"✓ 从数据项分析字段，共 {len(fields)} 个字段")
                for i, (field_id, value) in enumerate(fields.items()):
                    if i >= 3:  # 只显示前3个字段
                        break
                    print(f"  - {field_id}: {type(value).__name__}")

if __name__ == "__main__":
    # 配置unittest执行顺序和输出格式
    unittest.main(verbosity=2)