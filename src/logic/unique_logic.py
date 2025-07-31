from utils.utils import is_int, get_dict_template
import numpy as np
def valid_uniqueinfo(items: dict):
    """檢查受款人資訊是否正確
    
    Args:
        items:
    Returns:
        dict:
        
    """
    result = get_dict_template("unique_check")

    status, info, message = is_unique(items)
    result["status"]["status"] = status
    result["status"]["info"] = info
    result["status"]["message"] = message
    return result

def is_unique(items:dict):
    unique_list = []
    for k, v in items.items():
        if v != '':
            unique_list.append(k)

    if len(unique_list) != 1:
        return False, unique_list, f"多筆金額在同一行 {unique_list}"
    else:
        return True, unique_list[0], unique_list[0]