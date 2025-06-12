def match_student(**kwargs):
    """
    根据学生的数据匹配大学或国际学校。
    
    参数:
    **kwargs: 关键字参数
        - application_choice: "大学" 或 "国际学校"
        - academic_percentage: 学术成绩百分比
        - gaokao_score: 高考成绩 (如果没有则为None)
        - ielts_score: 雅思成绩 (如果没有则为None)
        - toefl_score: 托福成绩 (如果没有则为None)
        - det_score: DET成绩 (如果没有则为None)
        - language_pass: 学生是否通过学校语言测试
        - has_high_school_cert: 学生是否拥有高中毕业证书
        - has_international_school_experience: 学生是否有国际学校学习经验
        - budget_per_year: 年度教育预算(单位:SGD)
    
    返回:
    - 包含匹配结果的字典
    """
    result = {}
    
    application_choice = kwargs.get('application_choice')
    
    if application_choice == "申请私立大学本科":
        university_result = match_universities(**kwargs)
        result.update(university_result)
    
    elif application_choice == "国际学校":
        matched_schools = match_international_schools(**kwargs)
        result["matched_international_schools"] = matched_schools
    
    return result


def match_universities(**kwargs):
    """根据学生的学术成绩和语言能力匹配大学。"""
    result = {}
    
    # 获取参数并转换类型
    academic_percentage_raw = kwargs.get('academic_percentage', 0)
    gaokao_score_raw = kwargs.get('gaokao_score')
    ielts_score_raw = kwargs.get('ielts_score')
    toefl_score_raw = kwargs.get('toefl_score')
    det_score_raw = kwargs.get('det_score')
    language_pass = kwargs.get('language_pass', False)
    has_high_school_cert = kwargs.get('has_high_school_cert', False)
    
    # 转换学术成绩为数字 (处理百分比)
    try:
        if isinstance(academic_percentage_raw, str):
            # 去除可能的百分号
            academic_percentage_str = academic_percentage_raw.replace('%', '')
            academic_percentage = float(academic_percentage_str)
        else:
            academic_percentage = float(academic_percentage_raw) if academic_percentage_raw is not None else 0
    except (ValueError, TypeError):
        print(f"警告: 无法转换学术成绩 '{academic_percentage_raw}' 为数字，默认为0")
        academic_percentage = 0
    
    # 转换高考分数为数字
    try:
        gaokao_score = int(gaokao_score_raw) if gaokao_score_raw is not None else None
    except (ValueError, TypeError):
        print(f"警告: 无法转换高考成绩 '{gaokao_score_raw}' 为数字，设为None")
        gaokao_score = None
    
    # 转换雅思分数为数字
    try:
        ielts_score = float(ielts_score_raw) if ielts_score_raw is not None else None
    except (ValueError, TypeError):
        print(f"警告: 无法转换雅思成绩 '{ielts_score_raw}' 为数字，设为None")
        ielts_score = None
    
    # 转换托福分数为数字
    try:
        toefl_score = int(toefl_score_raw) if toefl_score_raw is not None else None
    except (ValueError, TypeError):
        print(f"警告: 无法转换托福成绩 '{toefl_score_raw}' 为数字，设为None")
        toefl_score = None
    
    # 转换DET分数为数字
    try:
        det_score = int(det_score_raw) if det_score_raw is not None else None
    except (ValueError, TypeError):
        print(f"警告: 无法转换DET成绩 '{det_score_raw}' 为数字，设为None")
        det_score = None
    
    # 输出转换后的值，便于调试
    print(f"转换后的值: academic_percentage={academic_percentage}, gaokao_score={gaokao_score}")
    print(f"转换后的值: ielts_score={ielts_score}, toefl_score={toefl_score}, det_score={det_score}")
    
    # 检查第一个条件：顶尖公立大学
    if academic_percentage > 80 or (gaokao_score is not None and gaokao_score > 600):
        if ((ielts_score is not None and 6.5 <= ielts_score <= 9.0) or 
            (toefl_score is not None and 79 <= toefl_score <= 120) or 
            (det_score is not None and det_score >= 105)):
            result["matched_universities"] = ["新加坡国立大学", "新加坡南洋理工大学"]
            return result
    
    # 检查第二个条件：其他公立大学
    if 75 <= academic_percentage <= 80 or (gaokao_score is not None and 520 <= gaokao_score <= 600):
        if ((ielts_score is not None and 6.0 <= ielts_score <= 9.0) or 
            (toefl_score is not None and 60 <= toefl_score <= 120) or 
            (det_score is not None and det_score >= 95)):
            result["matched_universities"] = ["新加坡管理大学", "新加坡科技设计大学"]
            return result
    
    # 如果学生不符合公立大学要求，检查私立大学的匹配条件
    # 第三级别私立大学
    if 70 <= academic_percentage < 75 or (gaokao_score is not None and 450 <= gaokao_score < 520):
        matched_universities = ["英国伯明翰大学", "澳大利亚皇家墨尔本理工大学", "爱尔兰都柏林大学"]
        path_to_university = determine_path_for_private_university(**kwargs)
        result["matched_universities"] = matched_universities
        result["path_to_university"] = path_to_university
        return result
    
    # 第四级别私立大学
    if 65 <= academic_percentage < 70 or (gaokao_score is not None and 400 <= gaokao_score < 450):
        matched_universities = ["澳大利亚伍伦贡大学", "澳洲纽卡斯尔大学", "澳大利亚科廷大学", "新西兰梅西大学", "乐卓博大学"]
        path_to_university = determine_path_for_private_university(**kwargs)
        result["matched_universities"] = matched_universities
        result["path_to_university"] = path_to_university
        return result
    
    # 第五级别私立大学
    if 60 <= academic_percentage < 65 or (gaokao_score is not None and 350 <= gaokao_score < 400):
        matched_universities = ["英国考文垂大学", "澳大利亚莫道克大学", "英国诺比森亚大学", "英国斯特灵大学"]
        path_to_university = determine_path_for_private_university(**kwargs)
        result["matched_universities"] = matched_universities
        result["path_to_university"] = path_to_university
        return result
    
    # 如果没有匹配到任何大学
    result["matched_universities"] = []
    return result


def determine_path_for_private_university(**kwargs):
    """
    根据语言能力和高中毕业情况确定申请私立大学的学生的路径。
    """
    # 获取参数并转换类型
    ielts_score_raw = kwargs.get('ielts_score')
    toefl_score_raw = kwargs.get('toefl_score')
    det_score_raw = kwargs.get('det_score')
    language_pass = kwargs.get('language_pass', False)
    has_high_school_cert = kwargs.get('has_high_school_cert', False)
    
    # 转换雅思分数为数字
    try:
        ielts_score = float(ielts_score_raw) if ielts_score_raw is not None else None
    except (ValueError, TypeError):
        print(f"警告: 无法转换雅思成绩 '{ielts_score_raw}' 为数字，设为None")
        ielts_score = None
    
    # 转换托福分数为数字
    try:
        toefl_score = int(toefl_score_raw) if toefl_score_raw is not None else None
    except (ValueError, TypeError):
        print(f"警告: 无法转换托福成绩 '{toefl_score_raw}' 为数字，设为None")
        toefl_score = None
    
    # 转换DET分数为数字
    try:
        det_score = int(det_score_raw) if det_score_raw is not None else None
    except (ValueError, TypeError):
        print(f"警告: 无法转换DET成绩 '{det_score_raw}' 为数字，设为None")
        det_score = None
    
    # 条件1：语言不达标 + 无高中毕业证书
    if ((ielts_score is not None and ielts_score < 5.5) or 
        (toefl_score is not None and toefl_score < 59) or 
        (det_score is not None and det_score < 100) or 
        not language_pass) and not has_high_school_cert:
        return "进入语言班随后升入预科班"
    
    # 条件2：语言不达标 + 有高中毕业证书
    elif ((ielts_score is not None and ielts_score < 5.5) or 
          (toefl_score is not None and toefl_score < 59) or 
          (det_score is not None and det_score < 100) or 
          not language_pass) and has_high_school_cert:
        return "进入语言班随后升入国际大一"
    
    # 条件3：语言中等 + 无高中毕业证书
    elif ((ielts_score is not None and ielts_score == 5.5) or 
          (toefl_score is not None and 46 <= toefl_score < 59) or 
          (det_score is not None and 85 <= det_score < 100) or 
          language_pass) and not has_high_school_cert:
        return "进入预科班"
    
    # 条件4：语言达标 + 有高中毕业证书
    elif ((ielts_score is not None and 6.0 <= ielts_score <= 9.0) or 
          (toefl_score is not None and 60 <= toefl_score <= 120) or 
          (det_score is not None and det_score >= 95) or 
          language_pass) and has_high_school_cert:
        return "进入国际大一"
    
    return None


def match_international_schools(**kwargs):
    """
    根据学生的学术成绩、国际学校经验和预算匹配国际学校。
    
    参数:
    **kwargs: 关键字参数
        - academic_percentage: 学术成绩百分比
        - has_international_school_experience: 学生是否有国际学校学习经验
        - budget_per_year: 年度教育预算(单位:SGD)
    
    返回:
    - 匹配的国际学校列表
    """
    academic_percentage = kwargs.get('academic_percentage', 0)
    has_international_school_experience = kwargs.get('has_international_school_experience', False)
    budget_per_year = kwargs.get('budget_per_year', 0)
    
    # 条件1：高学术成绩或有国际学校经验 + 高预算
    if (academic_percentage > 70 or has_international_school_experience) and budget_per_year >= 100000:
        return ["UWC", "东陵信托国际学校", "美国国际学校", "德威国际学校", "北伦敦伦敦国际学校"]
    
    # 条件2：中等学术成绩 + 中等预算
    elif academic_percentage > 50 and 50000 <= budget_per_year <= 90000:
        return ["斯坦福美国国际学校", "加拿大国际学校", "NPS国际学校", "澳洲国际学校", "布莱顿国际学校", "多佛国际学校"]
    
    # 条件3：低学术成绩 + 低预算
    elif academic_percentage < 50 and budget_per_year < 50000:
        return ["伊顿国际学校", "米德尔顿国际学校", "茵维特国际学校", "海外家庭学校", "莱仕国际学校", "环印国际学校", "壹世界国际学校", "汉合国际学校"]
    
    return []
