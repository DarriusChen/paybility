import re

from datetime import datetime
from utils.utils import is_int, get_dict_template
# 申請人/受款人檢查邏輯


def valid_recipientinfo(items:list):
    """檢查受款人資訊是否正確
    
    Args:
        items: list[name, id_name, id_bank, id_branch, account]
        result: dict{}
    Returns:
        result: dict{}
        
    """
    result = get_dict_template("recipient_check")

    name, id_name, id_bank, id_branch, account = items

    status, info, message = is_name_valid(name)
    result['sub_status']['matching_number']['status'] = status
    result['sub_status']['matching_number']['info'] = info
    result['sub_status']['matching_number']['message'] = message

    status, info, message = check_ID(id_name)
    result['sub_status']['id_name']['status'] = status
    result['sub_status']['id_name']['info'] = info
    result['sub_status']['id_name']['message'] = message

    status, info, message = is_bank_vaild(id_bank)
    result['sub_status']['id_bank']['status'] = status
    result['sub_status']['id_bank']['info'] = info
    result['sub_status']['id_bank']['message'] = message

    status, info, message = is_branch_vaild(id_branch)
    result['sub_status']['id_branch']['status'] = status
    result['sub_status']['id_branch']['info'] = info
    result['sub_status']['id_branch']['message'] = message

    status, info, message = is_account_vaild(id_branch)
    result['sub_status']['account']['status'] = status
    result['sub_status']['account']['info'] = info
    result['sub_status']['account']['message'] = message
    

    if (result['sub_status']['matching_number']['status'] and
        result['sub_status']['id_name']['status'] and
        result['sub_status']['id_bank']['status'] and 
        result['sub_status']['id_branch']['status'] and 
        result['sub_status']['account']['status']):

        result["status"]["status"] = True
        result["status"]["info"] = None
        result["status"]["message"] = "✅ 受款人/申請人格式正確"
    else:
        result["status"]["status"] = False
        result["status"]["info"] = None
        result["status"]["message"] = "❌ 受款人/申請人格式錯誤"
        
    return result

# name check 
def is_name_valid(name):
    if isinstance(name, str):   
        return True, name, "✅"
    else:
        return False, str(name), "❌"

# ID Code check
letter_code_map = {
    'A': 10,  # 台北市
    'B': 11,  # 台中市
    'C': 12,  # 基隆市
    'D': 13,  # 台南市
    'E': 14,  # 高雄市
    'F': 15,  # 新北市
    'G': 16,  # 宜蘭縣
    'H': 17,  # 桃園市
    'I': 34,  # 嘉義市
    'J': 18,  # 新竹縣
    'K': 19,  # 苗栗縣
    'L': 20,  # 台中縣
    'M': 21,  # 南投縣
    'N': 22,  # 彰化縣
    'O': 35,  # 新竹市
    'P': 23,  # 雲林縣
    'Q': 24,  # 嘉義縣
    'R': 25,  # 台南縣
    'S': 26,  # 高雄縣
    'T': 27,  # 屏東縣
    'U': 28,  # 花蓮縣
    'V': 29,  # 台東縣
    'W': 32,  # 金門縣
    'X': 30,  # 澎湖縣
    'Y': 31,  # 陽明山管理局（已廢）
    'Z': 33   # 連江縣
}

def get_letter_digits(letter):
    number = letter_code_map[letter.upper()]
    return [number // 10, number % 10]

def is_idformat_valid(id: str):
    """
    檢查是否為身分證格式：1 個大寫英文 + 9 個數字
    （自動將小寫轉為大寫）
    """
    id = id.upper()  # 將小寫字母轉成大寫
    pattern = r'^[A-Z][0-9]{9}$'
    return bool(re.match(pattern, id))
    
def check_ID(id = "A123456789"):
    print(f"ID: {id}")
    if is_idformat_valid(id):
        letter = str(id[0]).upper()
        number = id[1:]
        
        code = get_letter_digits(letter)
        code += number
        weight = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1, 1]
        
        total = 0
        for c, w in zip(code, weight):
            total += int(c) * int(w)
        
        if total % 10 == 0:
            # print("✅")
            return True, str(id), "✅"
        else:
            # print("❌")
            return False, None, "❌"

def is_bank_vaild(code: str):
    if is_int(code) and len(code) == 3:
        return True, code, "✅"
    else:
        return False, None, "❌"
    
def is_branch_vaild(code: str):
    if is_int(code) and len(code) == 4:
        return True, code, "✅"
    else:
        return False, None, "❌"

def is_account_vaild(code: str):
    if is_int(code) and len(code) <= 18:
        # padding to length 18
        code = "0" * (18 - len(code)) + code
        return True, code, "✅"
    else:
        return False, None, "❌"
    
def is_valid_date(date_str: str):
    try:
        parts = date_str.split('/')
        if len(parts) != 3:
            return False, "錯誤時間格式", "X"
        
        if len(parts[0]) == 3:
            year = int(parts[0]) + 1911  # 民國轉西元
        else:
            year = int(parts[0]) # 西元年
            
        datetime.strptime(f"{year}/{parts[1]}/{parts[2]}", "%Y/%m/%d")
        return True, f"{year}/{parts[1]}/{parts[2]}", "✅"
    except ValueError as e:
        return False, e, "❌"
    
