from datetime import datetime
from utils.utils import is_int, get_dict_template


def valid_dateinfo(dates: list):
    """檢查轉租約/租賃契約資訊是否正確
    
    Args:
        items:
    Returns:
        dict:
        
    """
    result = get_dict_template("date_check")

    status, info, message = is_valid_date(dates[0], "start")
    result['sub_status']['start']['status'] = status
    result['sub_status']['start']['info'] = info
    result['sub_status']['start']['message'] = message

    status, info, message = is_valid_date(dates[-1], "end")
    result['sub_status']['end']['status'] = status
    result['sub_status']['end']['info'] = info
    result['sub_status']['end']['message'] = message

    if (result['sub_status']['start']['status'] and 
        result['sub_status']['end']['status']):

        result["status"]["status"] = True
        result["status"]["info"] = None
        result["status"]["message"] = "✅ 時間格式正確"
    else:
        result["status"]["status"] = False
        result["status"]["info"] = None
        result["status"]["message"] = "❌ 時間格式錯誤"

    return result


def is_valid_date(date_str: str, flag: str):
    try:
        parts = date_str.split('/')
        if len(parts) != 3:
            return False, None, f"❌ {flag}錯誤時間格式"
        
        if len(parts[0]) == 3:
            year = int(parts[0]) + 1911  # 民國轉西元
        else:
            year = int(parts[0]) # 西元年
            
        datetime.strptime(f"{year}/{parts[1]}/{parts[2]}", "%Y/%m/%d")
        return True, f"{year}/{parts[1]}/{parts[2]}", f"✅ {flag}時間格式正確"
    except ValueError as e:
        return False, e, f"❌ {flag}時間錯誤"