import requests
import json
import time
from Match_Algo import match_student

# Huobanyun API Configuration - Updated to OpenAPI V1
API_BASE_URL = "https://api.huoban.com/openapi/v1"
APP_SECRET = "wPCoGnaYtQrNXoWv3I0VOrKnYQpOU8XNSyr5OzuJ"  # API密钥
SPACE_ID = "4000000007763686"  # 空间ID

# 表格配置 (替换为实际的表格ID)
STUDENT_TABLE_1_ID = "2100000065598053"  # 第一个学生表ID
STUDENT_TABLE_2_ID = "2100000065736402"  # 第二个学生表ID

# 大学表格配置 - 修改为三个不同类型的大学表
UNIVERSITY_TABLES = {
    "private": "2100000065741189",       # 私立大学数据表格
    "public_graduate": "2100000065744137", # 公立大学硕博阶段数据表格
    "public_undergrad": "2100000065744831" # 公立大学本科数据表格
}

INTERNATIONAL_SCHOOL_TABLE_ID = "intl_school_table_id"  # 国际学校表ID
MATCH_RESULT_TABLE_ID = "match_result_table_id"  # 存放匹配结果的表ID

class HuobanyunAPI:
    def __init__(self, app_secret):
        self.app_secret = app_secret
        self.token = None
        self.token_expires = 0
        self.field_configurations = {}  # 缓存表格字段配置

    def get_token(self):
        """获取访问令牌"""
        if self.token and time.time() < self.token_expires:
            return self.token

        url = f"{API_BASE_URL}/token/get"
        payload = {
            # 如果仅使用app_secret的认证方式，根据API要求修改以下参数
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("data", {}).get("token")
            # 令牌有效期通常在响应中提供，这里假设为2小时
            self.token_expires = time.time() + 7200
            return self.token
        else:
            raise Exception(f"获取令牌失败: {response.text}")

    def api_request(self, endpoint, payload=None):
        """发送API请求 - 更新为使用POST请求和Open-Authorization头"""
        token = self.get_token()
        headers = {
            "Open-Authorization": token,
            "Content-Type": "application/json"
        }
        
        url = f"{API_BASE_URL}/{endpoint}"
        
        # 所有请求都是使用POST
        if payload is None:
            payload = {}
            
        response = requests.post(url, headers=headers, json=payload)
            
        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            raise Exception(f"API请求失败: {response.text}")

    def get_table_list(self):
        """获取表格列表"""
        endpoint = "table/list"
        payload = {
            "space_id": SPACE_ID
        }
        return self.api_request(endpoint, payload)

    def get_table_details(self, table_id=None):
        """获取表格详细信息和字段配置"""
        endpoint = "table/"
        payload = {}
        if table_id:
            payload["table_id"] = table_id
        return self.api_request(endpoint, payload)

    def get_field_configurations(self, table_id):
        """获取并缓存表格的字段配置"""
        if table_id not in self.field_configurations:
            table_details = self.get_table_details(table_id)
            # 假设字段配置在响应的fields属性中
            self.field_configurations[table_id] = table_details.get("fields", [])
        return self.field_configurations[table_id]

    def get_table_item(self, item_id):
        """获取单个数据项"""
        endpoint = "item/"
        payload = {
            "item_id": item_id
        }
        return self.api_request(endpoint, payload)

    def get_table_items(self, table_id, limit=20, offset=0, filter_conditions=None, order=None):
        """获取表格中的数据项"""
        endpoint = "item/list"
        
        payload = {
            "table_id": table_id,
            "limit": limit,
            "offset": offset,
            "with_field_config": 0
        }
        
        if filter_conditions:
            payload["filter"] = filter_conditions
        
        if order:
            payload["order"] = order
        else:
            # 默认按创建时间倒序排序
            payload["order"] = {
                "field_id": "created_on",
                "type": "desc"
            }
            
        return self.api_request(endpoint, payload)
    
    def create_item(self, table_id, fields):
        """在表格中创建新数据项"""
        endpoint = "item/create"
        payload = {
            "table_id": table_id,
            "fields": fields
        }
        return self.api_request(endpoint, payload)
    
    def update_item(self, item_id, fields):
        """更新表格中的数据项"""
        endpoint = "item/update"
        payload = {
            "item_id": item_id,
            "fields": fields
        }
        return self.api_request(endpoint, payload)

def get_field_mappings(huoban_api, table_id, field_mapping_names):
    """
    根据字段名称获取对应的字段ID
    这对于初始设置非常有用
    """
    field_configs = huoban_api.get_field_configurations(table_id)
    field_mappings = {}
    
    # 遍历所有字段配置
    for field in field_configs:
        field_name = field.get("name", "")
        field_id = field.get("field_id", "")
        
        # 如果这个字段名在我们需要映射的列表中
        if field_name in field_mapping_names.values():
            # 找到对应的key
            for key, value in field_mapping_names.items():
                if value == field_name:
                    field_mappings[key] = field_id
                    break
    
    return field_mappings

def get_all_students(huoban_api):
    """从两个学生表中获取所有学生数据"""
    students = []
    
    # 字段名称映射 - 这些是实际的字段名称，将用于查询字段ID
    field_mapping_names = {
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
    }
    
    # 获取第一个表的字段ID映射
    field_mappings_table1 = get_field_mappings(huoban_api, STUDENT_TABLE_1_ID, field_mapping_names)
    
    # 获取第二个表的字段ID映射
    field_mappings_table2 = get_field_mappings(huoban_api, STUDENT_TABLE_2_ID, field_mapping_names)
    
    # 从第一个学生表获取数据
    table1_response = huoban_api.get_table_items(STUDENT_TABLE_1_ID)
    table1_items = table1_response.get("items", [])
    for item in table1_items:
        student = map_student_fields(item, field_mappings_table1, table_type=1)
        if student:  # 确保所有必需字段都已提供
            students.append(student)
    
    # 从第二个学生表获取数据
    table2_response = huoban_api.get_table_items(STUDENT_TABLE_2_ID)
    table2_items = table2_response.get("items", [])
    for item in table2_items:
        student = map_student_fields(item, field_mappings_table2, table_type=2)
        if student:  # 确保所有必需字段都已提供
            students.append(student)
    
    return students

def map_student_fields(item, field_mappings, table_type):
    """
    从原始数据项映射学生字段
    使用动态获取的字段ID
    """
    data = {}
    fields = item.get("fields", {})
    
    # 必需的字段
    required_fields = ["application_choice", "academic_percentage"]
    
    try:
        # 映射基本字段
        for key, field_id in field_mappings.items():
            if field_id in fields:
                data[key] = fields[field_id]
        
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

def get_university_data(huoban_api):
    """
    从三个不同的大学表获取大学数据
    返回格式化的大学数据，包括类型信息
    """
    university_data = {
        "private": [],
        "public_graduate": [],
        "public_undergrad": []
    }
    
    # 为每个表定义字段映射
    university_field_mapping = {
        "name": "大学名称",
        "admission_requirements": "入学要求",
        "tuition_fees": "学费",
        # 根据需要添加更多字段
    }
    
    # 获取私立大学数据
    private_table_id = UNIVERSITY_TABLES["private"]
    private_field_mappings = get_field_mappings(huoban_api, private_table_id, university_field_mapping)
    private_universities = huoban_api.get_table_items(private_table_id)
    for uni in private_universities.get("items", []):
        uni_data = map_university_fields(uni, private_field_mappings)
        if uni_data:
            uni_data["type"] = "private"
            university_data["private"].append(uni_data)
    
    # 获取公立大学硕博数据
    grad_table_id = UNIVERSITY_TABLES["public_graduate"]
    grad_field_mappings = get_field_mappings(huoban_api, grad_table_id, university_field_mapping)
    grad_universities = huoban_api.get_table_items(grad_table_id)
    for uni in grad_universities.get("items", []):
        uni_data = map_university_fields(uni, grad_field_mappings)
        if uni_data:
            uni_data["type"] = "public_graduate"
            university_data["public_graduate"].append(uni_data)
    
    # 获取公立大学本科数据
    undergrad_table_id = UNIVERSITY_TABLES["public_undergrad"]
    undergrad_field_mappings = get_field_mappings(huoban_api, undergrad_table_id, university_field_mapping)
    undergrad_universities = huoban_api.get_table_items(undergrad_table_id)
    for uni in undergrad_universities.get("items", []):
        uni_data = map_university_fields(uni, undergrad_field_mappings)
        if uni_data:
            uni_data["type"] = "public_undergrad"
            university_data["public_undergrad"].append(uni_data)
    
    return university_data

def map_university_fields(item, field_mappings):
    """
    从原始数据项映射大学字段
    使用动态获取的字段ID
    """
    data = {}
    fields = item.get("fields", {})
    
    try:
        # 映射基本字段
        for key, field_id in field_mappings.items():
            if field_id in fields:
                data[key] = fields[field_id]
        
        # 添加大学ID以便需要时引用
        data["university_id"] = item.get("item_id")
        
        return data
        
    except Exception as e:
        print(f"映射大学字段时出错: {e}")
        return None

def match_all_students(huoban_api, students):
    """为所有学生执行匹配"""
    results = []
    
    # 获取大学数据，只需获取一次
    university_data = get_university_data(huoban_api)
    
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
        
        # 根据申请类型选择合适的大学数据集
        application_type = student.get('application_choice', '').lower()
        
        # 添加大学数据到匹配参数
        if 'undergraduate' in application_type or 'bachelor' in application_type:
            match_params['university_data'] = {
                'private': university_data['private'],
                'public': university_data['public_undergrad']
            }
        elif 'graduate' in application_type or 'master' in application_type or 'doctoral' in application_type or 'phd' in application_type:
            match_params['university_data'] = {
                'private': university_data['private'],
                'public': university_data['public_graduate']
            }
        else:
            # 如果申请类型不明确，使用所有大学数据
            match_params['university_data'] = {
                'private': university_data['private'],
                'public': university_data['public_undergrad'] + university_data['public_graduate']
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
    
    # 获取结果表的字段配置
    field_mapping_names = {
        "student_id": "学生ID",
        "student_table_id": "学生表格ID",
        "matched_universities": "匹配大学",
        "path_to_university": "入学路径",
        "matched_international_schools": "匹配国际学校"
    }
    
    field_mappings = get_field_mappings(huoban_api, MATCH_RESULT_TABLE_ID, field_mapping_names)
    
    # 准备要保存的数据
    fields = {}
    
    # 使用动态字段ID
    if "student_id" in field_mappings:
        fields[field_mappings["student_id"]] = result_entry["student_id"]
    if "student_table_id" in field_mappings:
        fields[field_mappings["student_table_id"]] = result_entry["student_table_id"]
    
    # 根据申请类型添加匹配结果
    if "matched_universities" in match_result and "matched_universities" in field_mappings:
        fields[field_mappings["matched_universities"]] = ", ".join(match_result["matched_universities"])
        if "path_to_university" in match_result and "path_to_university" in field_mappings:
            fields[field_mappings["path_to_university"]] = match_result["path_to_university"]
    
    elif "matched_international_schools" in match_result and "matched_international_schools" in field_mappings:
        fields[field_mappings["matched_international_schools"]] = ", ".join(match_result["matched_international_schools"])
    
    # 创建匹配结果记录
    try:
        huoban_api.create_item(MATCH_RESULT_TABLE_ID, fields)
        print(f"已为学生 {result_entry['student_id']} 保存匹配结果")
    except Exception as e:
        print(f"保存匹配结果时发生错误: {e}")

def main():
    # 初始化API客户端，移除了APP_ID参数
    huoban_api = HuobanyunAPI(APP_SECRET)
    
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
