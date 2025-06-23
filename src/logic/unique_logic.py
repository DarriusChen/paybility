from utils.utils import is_int, get_dict_template
import numpy as np
def valid_uniqueinfo(items: list, names: list):
    """檢查受款人資訊是否正確
    
    Args:
        items:
    Returns:
        dict:
        
    """
    result = get_dict_template("unique_check")

    status, info, message = is_unique(items)
    result['sub_status']['unique']['status'] = status
    result['sub_status']['unique']['info'] = info
    result['sub_status']['unique']['message'] = message

    if result['sub_status']['unique']['status']:
        result["status"]["status"] = True
        result["status"]["info"] = None
        result["status"]["message"] = f"✅ {result['sub_status']['unique']['info']}格式正確"
    else:
        result["status"]["status"] = False
        result["status"]["info"] = None
        result["status"]["message"] = f"❌ {result['sub_status']['unique']['info']}格式錯誤"
    return result

def is_unique(items: list):
    
    if set(items) == {1}:
    # casetype
        if max(items) > 1:
            return False, "案件", "❌ 案件不唯一"
        else:
            return True, "案件", "✅ 案件唯一"
    else: 
    # cashtype
        if len([x for x in items if x not in [0, np.nan]]) > 1:
            return False, "費用", "❌ 費用不唯一"
        else:
            return True, "費用", "✅ 費用唯一"
