from utils.utils import Result
import numpy as np
def valid_uniquecase(result: Result):
    """檢查案件唯一性
    
    Args:
        items:
    Returns:
        dict:
        
    """
    item_list = result.get_caselist()
    unique_list = []
    for i in item_list:
        if result.get_row(i) != '':
            unique_list.append(i)

    if len(unique_list) != 1:
        result.insert_rowerror(f"案件", f"多筆案件在同一行 {unique_list}")
    else:
        result.insert_rowinfo("案件", unique_list[0])

def valid_uniquecash(result: Result):
    """檢查費用唯一性
    
    Args:
        items:
    Returns:
        dict:
        
    """
    item_list = result.get_cashlist()
    unique_list = []
    for i in item_list:
        if result.get_row(i) != '':
            unique_list.append(i)

    if len(unique_list) != 1:
        result.insert_rowerror(f"費用", f"多筆費用在同一行 {unique_list}")
    else:
        result.insert_rowinfo("費用", unique_list[0])

