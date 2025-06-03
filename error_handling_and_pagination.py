def get_all_paginated_items(huoban_api, table_id, filter_conditions=None):
    """
    获取表格中的所有数据项，处理分页
    """
    all_items = []
    page = 1
    limit = 100
    
    while True:
        try:
            results = huoban_api.get_table_items(table_id, limit=limit, page=page, filter_conditions=filter_conditions)
            items = results.get("items", [])
            
            if not items:
                break
                
            all_items.extend(items)
            
            # 检查是否还有更多页
            total = results.get("total", 0)
            if len(all_items) >= total:
                break
                
            page += 1
            
        except Exception as e:
            print(f"获取第 {page} 页数据时出错: {e}")
            break
    
    return all_items

def retry_api_call(func, max_retries=3, *args, **kwargs):
    """
    重试API调用的辅助函数
    """
    retry_count = 0
    while retry_count < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            retry_count += 1
            wait_time = 2 ** retry_count  # 指数退避
            print(f"API调用失败，{wait_time}秒后重试 ({retry_count}/{max_retries}): {e}")
            time.sleep(wait_time)
    
    raise Exception(f"达到最大重试次数 ({max_retries})，操作失败")