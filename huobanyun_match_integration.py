import requests
import json
import time
from Match_Algo import match_student

# Huobanyun API Configuration
API_BASE_URL = "https://api.huoban.com/openapi/v1"
APP_SECRET = "wPCoGnaYtQrNXoWv3I0VOrKnYQpOU8XNSyr5OzuJ"  # API密钥
SPACE_ID = "4000000007763686"  # 空间ID

# 表格配置
STUDENT_TABLE_1_ID = "2100000065598053"  # 第一个学生表ID
STUDENT_TABLE_2_ID = "2100000065736402"  # 第二个学生表ID

# 大学表格配置 - 三个不同类型的大学表
UNIVERSITY_TABLES = {
    "private": "2100000065741189",       # 私立大学数据表格
    "public_graduate": "2100000065744137", # 公立大学硕博阶段数据表格
    "public_undergrad": "2100000065744831" # 公立大学本科数据表格
}

INTERNATIONAL_SCHOOL_TABLE_ID = "2100000066695624"  # 国际学校表ID
MATCH_RESULT_TABLE_ID = "2100000066645204"  # 存放匹配结果的表ID

class HuobanyunAPI:
    def __init__(self, app_secret):
        self.app_secret = app_secret
        self.field_configurations = {}  # 缓存表格字段配置

    def get_headers(self):
        """获取API请求头部"""
        return {
            "Open-Authorization": f"Bearer {self.app_secret}",
            "Content-Type": "application/json"
        }

    def api_request(self, method, url, payload=None, debug=False):
        """发送API请求"""
        headers = self.get_headers()
        
        if payload is None:
            payload = {}
        
        if debug:
            print(f"请求: {method} {url}")
            print(f"载荷: {json.dumps(payload)}")
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=payload)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=payload)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=payload)
            else:
                raise ValueError(f"不支持的请求方法: {method}")
            
            if debug:
                print(f"状态码: {response.status_code}")
                print(f"响应: {response.text[:200]}{'...' if len(response.text) > 200 else ''}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:  # 确保业务逻辑成功
                    return data.get("data", {})  # 直接返回 data 部分
                else:
                    error_msg = f"API业务逻辑错误: {data.get('message', 'Unknown error')}"
                    if debug:
                        print(f"错误: {error_msg}")
                    raise Exception(error_msg)
            else:
                error_msg = f"API请求失败: {response.status_code} - {response.text}"
                if debug:
                    print(f"错误: {error_msg}")
                raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            if debug:
                print(f"请求异常: {e}")
            raise Exception(f"请求异常: {e}")
    
    def get_table_list(self):
        """获取表格列表"""
        url = f"{API_BASE_URL}/table/list"
        payload = {
            "space_id": SPACE_ID
        }
        return self.api_request("POST", url, payload)
    
    def get_table_details(self, table_id):
        """获取表格详细信息"""
        # 根据官方示例，URL是 /table/ 后面直接跟ID
        url = f"{API_BASE_URL}/table/{table_id}"
        return self.api_request("POST", url, {})
    
    def get_field_configurations(self, table_id):
        """获取并缓存表格的字段配置"""
        try:
            if table_id not in self.field_configurations:
                table_details = self.get_table_details(table_id)
                # 修复：正确获取API响应中的字段信息
                # 打印完整结构以便调试
                print(f"表格 {table_id} 详情结构:")
                print(json.dumps(table_details, indent=2, ensure_ascii=False)[:500] + "...")
                
                # 字段应该在 table.fields 路径下
                if "table" in table_details and "fields" in table_details["table"]:
                    self.field_configurations[table_id] = table_details["table"]["fields"]
                    print(f"成功获取 {len(self.field_configurations[table_id])} 个字段")
                else:
                    print(f"警告:未在API响应中找到字段配置,返回路径: {list(table_details.keys())}")
                    if "table" in table_details:
                        print(f"table键包含: {list(table_details['table'].keys())}")
                    self.field_configurations[table_id] = []
            return self.field_configurations[table_id]
        except Exception as e:
            print(f"获取字段配置时发生错误 (表格ID: {table_id}): {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_table_items(self, table_id, limit=None, filter_conditions=None):
        """获取表格中的项目"""
        url = f"{API_BASE_URL}/item/list"
        payload = {
            "table_id": table_id
        }
        
        # 添加分页限制
        if limit is not None:
            payload["limit"] = limit
        
        # 添加过滤条件
        if filter_conditions is not None:
            payload["filter"] = filter_conditions
        
        return self.api_request("POST", url, payload)

    def get_item_details(self, item_id):
        """获取单个项目详情"""
        url = f"{API_BASE_URL}/item/{item_id}"
        return self.api_request("POST", url, {})

    def create_item(self, table_id, fields):
        """创建新的表格项目"""
        url = f"{API_BASE_URL}/item"  # 注意没有斜杠
        payload = {
            "table_id": table_id,
            "fields": fields
        }
        return self.api_request("POST", url, payload)

    def update_item(self, item_id, fields):
        """更新已有的表格项目"""
        url = f"{API_BASE_URL}/item/{item_id}"
        payload = {
            "fields": fields
        }
        return self.api_request("PUT", url, payload)  # 注意这里是PUT请求

def get_field_mappings(huoban_api, table_id, field_mapping_names):
    """根据字段名称获取对应的字段ID"""
    try:
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
    except Exception as e:
        print(f"获取字段映射时发生错误 (表格ID: {table_id}): {e}")
        import traceback
        traceback.print_exc()
        return {}

def get_all_students(huoban_api):
    """从两个学生表中获取所有学生数据"""
    students = []
    
    # 字段名称映射 - 这些是实际的字段名称，将用于查询字段ID
    field_mapping_names = {
        "application_choice": "申请类型",
        "academic_percentage": "学术成绩",
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
    """从原始数据项映射学生字段"""
    data = {}
    fields = item.get("fields", {})
    
    try:
        print(f"处理学生记录: {item.get('item_id')}")
        print(f"字段映射: {field_mappings}")
        print(f"可用字段: {list(fields.keys())}")
        
        # 映射基本字段
        for key, field_id in field_mappings.items():
            if field_id in fields:
                field_value = fields[field_id]
                
                print(f"找到字段 '{key}' (ID: {field_id}) 值类型: {type(field_value)}")
                
                # 特殊处理选择类型字段
                if isinstance(field_value, dict) and "text" in field_value:
                    # 选择字段通常会包含 text 属性
                    data[key] = field_value["text"]
                    print(f"  处理选择字段: {field_value} -> {data[key]}")
                elif isinstance(field_value, list) and len(field_value) > 0 and isinstance(field_value[0], dict):
                    # 多选字段通常是字典列表
                    names = [item.get("name", "") for item in field_value if "name" in item]
                    data[key] = ", ".join(names) if names else ""
                    print(f"  处理多选字段: {field_value} -> {data[key]}")
                else:
                    data[key] = field_value
        
        # 确保必需字段存在
        required_fields = ["application_choice", "academic_percentage"]
        for field in required_fields:
            if field not in data or not data[field]:  # 检查空字符串
                print(f"学生记录缺少必需字段: {field}")
                return None
        
        # 添加学生ID以便之后更新匹配结果
        data["student_id"] = item.get("item_id")
        data["table_id"] = STUDENT_TABLE_1_ID if table_type == 1 else STUDENT_TABLE_2_ID
        
        # 输出最终映射结果
        print(f"最终映射结果: {data}")
        return data
        
    except Exception as e:
        print(f"映射学生字段时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_university_data(huoban_api):
    """从三个不同的大学表获取大学数据"""
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
    """从原始数据项映射大学字段"""
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
    
def get_international_school_data(huoban_api):
    """从国际学校表获取学校数据"""
    schools = []
    
    # 为国际学校表定义字段映射
    school_field_mapping = {
        "name": "学校名称",
        "admission_requirements": "入学要求",
        "tuition_fees": "学费",
        "curriculum": "课程体系",
        "language_requirements": "语言要求",
        "location": "地理位置",
        "school_type": "学校类型",
        "university_placement": "大学录取情况"
        # 根据表格后续可以添加更多字段
    }
    
    # 获取国际学校表的字段ID映射
    field_mappings = get_field_mappings(huoban_api, INTERNATIONAL_SCHOOL_TABLE_ID, school_field_mapping)
    
    # 获取国际学校数据
    schools_response = huoban_api.get_table_items(INTERNATIONAL_SCHOOL_TABLE_ID)
    for school in schools_response.get("items", []):
        school_data = map_intl_school_fields(school, field_mappings)
        if school_data:  # 确保数据有效
            schools.append(school_data)
    
    print(f"从国际学校表获取了 {len(schools)} 所学校")
    return schools

def map_intl_school_fields(item, field_mappings):
    """从原始数据项映射国际学校字段"""
    data = {}
    fields = item.get("fields", {})
    
    try:
        # 映射基本字段
        for key, field_id in field_mappings.items():
            if field_id in fields:
                data[key] = fields[field_id]
        
        # 确保学校名称存在
        if "name" not in data or not data["name"]:
            print("国际学校记录缺少必要的学校名称")
            return None
        
        # 添加学校ID以便需要时引用
        data["school_id"] = item.get("item_id")
        
        # 处理特定字段（如有必要）
        if "tuition_fees" in data and data["tuition_fees"] is not None:
            try:
                data["tuition_fees"] = float(data["tuition_fees"])
            except ValueError:
                print(f"警告：学校 '{data.get('name')}' 的学费无法转换为数字")
        
        return data
        
    except Exception as e:
        print(f"映射国际学校字段时出错: {e}")
        return None
    
def get_student_name(huoban_api, student_id, table_id):
    """获取学生姓名"""
    try:
        # 获取学生记录详情
        student_item = huoban_api.get_item_details(student_id)
        if not student_item:
            print(f"无法获取学生ID为 {student_id} 的详情")
            return None
        
        # 获取表格字段配置
        fields = huoban_api.get_field_configurations(table_id)
        name_field = next((f for f in fields if f.get("name") == "学生姓名"), None)
        
        if not name_field:
            print(f"表格 {table_id} 中没有找到学生姓名字段")
            return None
        
        name_field_id = name_field.get("field_id")
        if not name_field_id or name_field_id not in student_item.get("fields", {}):
            print(f"学生记录中没有姓名字段 {name_field_id}")
            return None
        
        student_name = student_item["fields"][name_field_id]
        return student_name
        
    except Exception as e:
        print(f"获取学生姓名时出错: {e}")
        return None
    
def update_match_result(huoban_api, result_entry):
    """检查是否已存在匹配结果，如果存在则更新，否则创建新记录"""
    # 提取匹配结果和学生信息
    match_result = result_entry["match_result"]
    student_id = result_entry["student_id"]
    
    print(f"\n=== 更新匹配结果 ===")
    print(f"学生ID: {student_id}")
    print(f"匹配结果: {match_result}")
    
    # 先获取学生姓名
    student_name = get_student_name(huoban_api, student_id, result_entry["student_table_id"])
    
    # 修改为匹配实际表格的字段名
    field_mapping_names = {
        "student_name": "学生姓名",  # 对应学生姓名字段
        "matched_schools": "配对学校名称"  # 对应配对学校名称字段
    }
    
    # 获取结果表的字段配置
    field_mappings = get_field_mappings(huoban_api, MATCH_RESULT_TABLE_ID, field_mapping_names)
    print(f"字段映射结果: {field_mappings}")
    
    # 准备要保存的数据
    fields = {}
    
    # 添加学生姓名
    if "student_name" in field_mappings and student_name:
        fields[field_mappings["student_name"]] = student_name
    
    # 提取匹配结果并合并到一个字段中
    matched_schools = []
    
    # 如果有匹配大学，添加到学校列表
    if "matched_universities" in match_result:
        universities = match_result["matched_universities"]
        if universities:  # 确保不是空列表
            path = match_result.get("path_to_university", "")
            if path:
                matched_schools.append(f"大学匹配: {', '.join(universities)} - 路径: {path}")
            else:
                matched_schools.append(f"大学匹配: {', '.join(universities)}")
    
    # 如果有匹配国际学校，添加到学校列表
    if "matched_international_schools" in match_result:
        schools = match_result["matched_international_schools"]
        if schools:  # 确保不是空列表
            matched_schools.append(f"国际学校匹配: {', '.join(schools)}")
    
    # 将所有匹配结果合并为一个字符串
    if matched_schools:
        match_text = "\n".join(matched_schools)
    else:
        match_text = "未找到匹配结果"
    
    # 添加匹配结果到配对学校名称字段
    if "matched_schools" in field_mappings:
        fields[field_mappings["matched_schools"]] = match_text
    
    print(f"要保存的字段: {fields}")
    
    # 如果没有任何字段匹配，添加默认字段避免API错误
    if not fields:
        print("警告: 没有任何字段匹配，添加学生姓名作为默认字段")
        # 获取学生姓名字段ID
        field_configs = huoban_api.get_field_configurations(MATCH_RESULT_TABLE_ID)
        for field in field_configs:
            if field.get("name") == "学生姓名":
                fields[field.get("field_id")] = student_name or "未知学生"
                break
    
    # 检查是否存在该学生的匹配结果 (基于学生姓名字段)
    student_name_field_id = field_mappings.get("student_name")
    existing_item_id = find_existing_match_result(huoban_api, student_name, student_name_field_id) if student_name_field_id else None
    
    try:
        if existing_item_id:
            # 如果存在，则更新记录
            print(f"更新现有记录 {existing_item_id}")
            result = huoban_api.update_item(existing_item_id, fields)
            print(f"已更新学生 {student_name} 的匹配结果")
        else:
            # 如果不存在，则创建新记录
            print(f"创建新记录")
            result = huoban_api.create_item(MATCH_RESULT_TABLE_ID, fields)
            print(f"已为学生 {student_name or student_id} 创建新的匹配结果")
        
    except Exception as e:
        print(f"更新或创建匹配结果时发生错误: {e}")
        import traceback
        traceback.print_exc()

def find_existing_match_result(huoban_api, student_name, student_name_field_id):
    """根据学生姓名查找是否已存在匹配结果"""
    if not student_name_field_id or not student_name:
        print("缺少学生姓名或字段ID,无法搜索现有匹配结果")
        return None
    
    # 构建过滤条件
    filter_conditions = {
        "conjunction": "and",
        "conditions": [
            {
                "field_id": student_name_field_id,
                "operator": "eq", 
                "values": [student_name]
            }
        ]
    }
    
    try:
        # 使用API搜索记录
        results = huoban_api.get_table_items(
            MATCH_RESULT_TABLE_ID, 
            limit=1,  # 我们只需要一条记录
            filter_conditions=filter_conditions
        )
        
        # 检查是否找到记录
        if results.get("items") and len(results["items"]) > 0:
            return results["items"][0]["item_id"]
        
        return None
        
    except Exception as e:
        print(f"查找现有匹配结果时发生错误: {e}")
        return None
    
def match_all_students(huoban_api, students):
    """为所有学生执行匹配"""
    results = []
    
    # 获取大学数据，只需获取一次
    university_data = get_university_data(huoban_api)
    
    # 获取国际学校数据，只需获取一次
    international_schools = get_international_school_data(huoban_api)
    
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
            'budget_per_year': student.get('budget_per_year', 0),
            'international_schools': international_schools  # 添加国际学校数据
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
        
        # 使用新函数更新或创建匹配结果
        update_match_result(huoban_api, result_entry)
        
        results.append(result_entry)
    
    return results

def check_all_tables():
    """检查所有相关表格是否可访问"""
    huoban_api = HuobanyunAPI(APP_SECRET)
    print("检查所有相关表格...")
    
    # 首先尝试获取所有表格列表，以验证API连接正常
    try:
        print("\n尝试获取空间内所有表格...")
        # 启用调试以查看详细请求和响应
        url = f"{API_BASE_URL}/table/list"
        payload = {"space_id": SPACE_ID}
        tables_response = huoban_api.api_request("POST", url, payload, debug=True)
        tables = tables_response.get("tables", [])
        print(f"✅ 成功! 找到 {len(tables)} 个表格")
        print("表格列表前5个:")
        for i, table in enumerate(tables[:5]):
            print(f"  {i+1}. {table.get('name', '未知')} (ID: {table.get('table_id', '未知')})")
    except Exception as e:
        print(f"❌ 获取表格列表失败: {e}")
    
    # 要检查的表格ID列表
    tables_to_check = [
        {"id": STUDENT_TABLE_1_ID, "description": "学生资料统计 (STUDENT_TABLE_1_ID)"},
        {"id": STUDENT_TABLE_2_ID, "description": "低龄学生资料 (STUDENT_TABLE_2_ID)"},
        {"id": UNIVERSITY_TABLES["private"], "description": "新加坡私立大学数据库 (private)"},
        {"id": UNIVERSITY_TABLES["public_graduate"], "description": "新加坡公立大学【硕博专业】2025 (public_graduate)"},
        {"id": UNIVERSITY_TABLES["public_undergrad"], "description": "新加坡公立本科申请 (public_undergrad)"},
        {"id": INTERNATIONAL_SCHOOL_TABLE_ID, "description": "国际学校表 (INTERNATIONAL_SCHOOL_TABLE_ID)"},
        {"id": MATCH_RESULT_TABLE_ID, "description": "匹配结果表 (MATCH_RESULT_TABLE_ID)"}
    ]
    
    for table in tables_to_check:
        try:
            print(f"\n检查表格: {table['description']} (ID: {table['id']})")
            # 启用调试以查看详细请求和响应
            url = f"{API_BASE_URL}/table/{table['id']}"
            details = huoban_api.api_request("POST", url, {}, debug=True)
            print(f"✅ 成功访问! 表名: {details.get('name', '未知')}")
            
            # 检查字段配置
            try:
                fields = details.get("fields", [])
                print(f"   字段数量: {len(fields)}")
                print("   前3个字段:")
                for i, field in enumerate(fields[:3]):
                    print(f"     - {field.get('name', '未知')} (类型: {field.get('type', '未知')})")
            except Exception as e:
                print(f"   ⚠️ 获取字段配置失败: {e}")
        except Exception as e:
            print(f"❌ 访问失败: {e}")

def main():
    # 初始化API客户端
    huoban_api = HuobanyunAPI(APP_SECRET)
    
    try:
        print("开始执行学生匹配流程...")
        
        # 获取学生数据
        students = get_all_students(huoban_api)
        print(f"共获取 {len(students)} 名学生记录")
        
        # 执行匹配
        match_results = match_all_students(huoban_api, students)
        print(f"已完成 {len(match_results)} 名学生的匹配")
        
        print("匹配流程执行完成！")
        return match_results
        
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()  # 打印详细堆栈跟踪
        return None

if __name__ == "__main__":
    # 添加调试输出
    print(f"使用API基础URL: {API_BASE_URL}")
    print(f"使用空间ID: {SPACE_ID}")
    print(f"APP_SECRET 长度: {len(APP_SECRET)} 字符")
    print(f"APP_SECRET 前5个字符: {APP_SECRET[:5]}...")
    
    check_all_tables()  # 首先进行表格检查
    # 如果表格检查成功，可以取消下面的注释来运行匹配
    main()
