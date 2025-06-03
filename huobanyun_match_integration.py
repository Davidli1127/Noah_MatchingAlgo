import requests
import json
import time
from Match_Algo import match_student

# Huobanyun API Configuration
API_BASE_URL = "https://api.huoban.com/v2"
APP_ID = "YOUR_APP_ID"  # 替换为你的应用ID
APP_SECRET = "YOUR_APP_SECRET"  # 替换为你的应用密钥

# 表格配置 (替换为实际的表格ID)
STUDENT_TABLE_1_ID = "student_table_1_id"  # 第一个学生表ID
STUDENT_TABLE_2_ID = "student_table_2_id"  # 第二个学生表ID
UNIVERSITY_TABLE_ID = "university_table_id"  # 大学表ID
INTERNATIONAL_SCHOOL_TABLE_ID = "intl_school_table_id"  # 国际学校表ID
MATCH_RESULT_TABLE_ID = "match_result_table_id"  # 存放匹配结果的表ID

class HuobanyunAPI:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.token = None
        self.token_expires = 0

    def get_token(self):
        """获取访问令牌"""
        if self.token and time.time() < self.token_expires:
            return self.token

        url = f"{API_BASE_URL}/token"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            # 令牌有效期通常在响应中提供，这里假设为2小时
            self.token_expires = time.time() + 7200
            return self.token
        else:
            raise Exception(f"获取令牌失败: {response.text}")

    def api_request(self, method, endpoint, params=None, data=None):
        """发送API请求"""
        token = self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{API_BASE_URL}/{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
            
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"API请求失败: {response.text}")

    def get_table_items(self, table_id, limit=100, page=1, filter_conditions=None):
        """获取表格中的数据项"""
        endpoint = f"tables/{table_id}/items"
        
        params = {
            "limit": limit,
            "page": page
        }
        
        if filter_conditions:
            params["filter"] = json.dumps(filter_conditions)
            
        return self.api_request("GET", endpoint, params=params)
    
    def create_item(self, table_id, item_data):
        """在表格中创建新数据项"""
        endpoint = f"tables/{table_id}/items"
        return self.api_request("POST", endpoint, data=item_data)
    
    def update_item(self, table_id, item_id, item_data):
        """更新表格中的数据项"""
        endpoint = f"tables/{table_id}/items/{item_id}"
        return self.api_request("PUT", endpoint, data=item_data)

def get_all_students(huoban_api):
    """从两个学生表中获取所有学生数据"""
    students = []
    
    # 从第一个学生表获取数据
    table1_items = huoban_api.get_table_items(STUDENT_TABLE_1_ID)
    for item in table1_items.get("items", []):
        student = map_student_fields(item, table_type=1)
        if student:  # 确保所有必需字段都已提供
            students.append(student)
    
    # 从第二个学生表获取数据
    table2_items = huoban_api.get_table_items(STUDENT_TABLE_2_ID)
    for item in table2_items.get("items", []):
        student = map_student_fields(item, table_type=2)
        if student:  # 确保所有必需字段都已提供
            students.append(student)
    
    return students

def map_student_fields(item, table_type):
    """
    从原始数据项映射学生字段
    注意：需要根据实际的字段名称进行调整
    """
    data = {}
    fields = item.get("fields", {})
    
    # 这里的字段名是假设的，需要根据实际情况调整
    field_mappings = {
        # 两个表可能具有不同的字段名映射
        1: {
            "application_choice": "申请类型",
            "academic_percentage": "学术成绩百分比",
            "gaokao_score": "高考成绩",
            "ielts_score": "雅思成绩",
            "toefl_score": "托福成绩",
            "det_score": "DET成绩",
            "language_pass": "通过语言测试",
            "has_high_school_cert": "拥有高中毕业证书",
            "has_international_school_experience": "有国际学校经验",
            "budget_per_year": "年度预算"
        },
        2: {
            # 第二个表的字段映射，如有不同
            "application_choice": "申请选择",
            "academic_percentage": "学术成绩",
            "gaokao_score": "高考分数",
            # ... 其他字段映射
        }
    }
    
    mapping = field_mappings.get(table_type, {})
    
    # 必需的字段
    required_fields = ["application_choice", "academic_percentage"]
    
    try:
        # 映射基本字段
        for key, field_name in mapping.items():
            if field_name in fields:
                data[key] = fields[field_name]
        
        # 确保必需字段存在
        for field in required_fields:
            if field not in data or data[field] is None:
                print(f"学生记录缺少必需字段: {field}")
                return None
        
        # 添加学生ID以便之后更新匹配结果
        data["student_id"] = item.get("item_id")
        data["table_id"] = STUDENT_TABLE_1_ID if table_type == 1 else STUDENT_TABLE_2_ID
        
        return data
        
    except Exception as e:
        print(f"映射学生字段时出错: {e}")
        return None

def match_all_students(huoban_api, students):
    """为所有学生执行匹配"""
    results = []
    
    for student in students:
        # 创建用于匹配的参数字典
        match_params = {
            'application_choice': student.get('application_choice'),
            'academic_percentage': student.get('academic_percentage'),
            'gaokao_score': student.get('gaokao_score'),
            'ielts_score': student.get('ielts_score'),
            'toefl_score': student.get('toefl_score'),
            'det_score': student.get('det_score'),
            'language_pass': student.get('language_pass', False),
            'has_high_school_cert': student.get('has_high_school_cert', False),
            'has_international_school_experience': student.get('has_international_school_experience', False),
            'budget_per_year': student.get('budget_per_year', 0)
        }
        
        # 调用匹配算法
        match_result = match_student(**match_params)
        
        # 存储结果
        result_entry = {
            "student_id": student["student_id"],
            "student_table_id": student["table_id"],
            "match_result": match_result
        }
        
        # 将匹配结果保存到Huobanyun
        save_match_result(huoban_api, result_entry)
        
        results.append(result_entry)
    
    return results

def save_match_result(huoban_api, result_entry):
    """将匹配结果保存到Huobanyun"""
    # 提取匹配结果
    match_result = result_entry["match_result"]
    
    # 准备要保存的数据
    # 注意：需要根据实际的字段名称进行调整
    item_data = {
        "fields": {
            "学生ID": result_entry["student_id"],
            "学生表格ID": result_entry["student_table_id"],
        }
    }
    
    # 根据申请类型添加匹配结果
    if "matched_universities" in match_result:
        item_data["fields"]["匹配大学"] = ", ".join(match_result["matched_universities"])
        if "path_to_university" in match_result:
            item_data["fields"]["入学路径"] = match_result["path_to_university"]
    
    elif "matched_international_schools" in match_result:
        item_data["fields"]["匹配国际学校"] = ", ".join(match_result["matched_international_schools"])
    
    # 创建匹配结果记录
    try:
        huoban_api.create_item(MATCH_RESULT_TABLE_ID, item_data)
        print(f"已为学生 {result_entry['student_id']} 保存匹配结果")
    except Exception as e:
        print(f"保存匹配结果时发生错误: {e}")

def main():
    # 初始化API客户端
    huoban_api = HuobanyunAPI(APP_ID, APP_SECRET)
    
    try:
        # 获取学生数据
        students = get_all_students(huoban_api)
        print(f"共获取 {len(students)} 名学生记录")
        
        # 执行匹配
        match_results = match_all_students(huoban_api, students)
        print(f"已完成 {len(match_results)} 名学生的匹配")
        
        return match_results
        
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        return None

if __name__ == "__main__":
    main()