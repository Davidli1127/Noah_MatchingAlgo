def get_university_details(huoban_api, university_names):
    """
    获取大学详细信息
    """
    # 构建过滤条件，查找名称在列表中的大学
    filter_conditions = {
        "conjunction": "or",
        "conditions": [{"field": "大学名称", "operator": "eq", "value": name} for name in university_names]
    }
    
    return huoban_api.get_table_items(UNIVERSITY_TABLE_ID, filter_conditions=filter_conditions)

def get_school_details(huoban_api, school_names):
    """
    获取国际学校详细信息
    """
    # 构建过滤条件，查找名称在列表中的学校
    filter_conditions = {
        "conjunction": "or",
        "conditions": [{"field": "学校名称", "operator": "eq", "value": name} for name in school_names]
    }
    
    return huoban_api.get_table_items(INTERNATIONAL_SCHOOL_TABLE_ID, filter_conditions=filter_conditions)

def update_student_with_matches(huoban_api, student_id, student_table_id, match_result):
    """
    更新学生记录，添加匹配结果
    """
    # 创建更新数据
    update_data = {
        "fields": {}
    }
    
    # 根据匹配结果类型添加字段
    if "matched_universities" in match_result:
        update_data["fields"]["匹配大学"] = ", ".join(match_result["matched_universities"])
        if "path_to_university" in match_result:
            update_data["fields"]["入学路径"] = match_result["path_to_university"]
    
    elif "matched_international_schools" in match_result:
        update_data["fields"]["匹配国际学校"] = ", ".join(match_result["matched_international_schools"])
    
    # 更新学生记录
    return huoban_api.update_item(student_table_id, student_id, update_data)