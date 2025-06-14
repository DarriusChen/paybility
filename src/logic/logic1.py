import re

from datetime import datetime
from utils.utils import is_int
# 
def check_unique(items: list):
    """檢查items在表中是否有唯一性
    
    Args:
        items: 表中內容的唯一性
    Returns:
        bool: True/False
        
    """
    
    
    return False



def check_recipientinfo(items: list):
    """檢查受款人資訊是否正確
    
    Args:
        items:
    Returns:
        dict:
        
    """
    return {}

# name check 
def is_name_valid(name):
    try:
        name = str(name)
        
        return name
    except:
        return "null"

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
            print("✅")
            return True
        else:
            print("❌")
            return False

def is_bankcode_vaild(code: str):
    if is_int(code) and len(code) == 3:
        return True, code, "O"
    else:
        return False, None, "X"
    
def is_branchcode_vaild(code: str):
    if is_int(code) and len(code) == 4:
        return True, code, "O"
    else:
        return False, None, "X"

def is_account_vaild(code: str):
    if is_int(code) and len(code) <= 18:
        # padding to length 18
        code = "0" * (18 - len(code)) + code
        return True, code, "O"
    else:
        return False, None, "X"
    
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
        return True, f"{year}/{parts[1]}/{parts[2]}", "O"
    except ValueError as e:
        return False, e, "X"
    
def period_check(period: str, total_period: str, period_type: str):
    
    """檢查期數是否正確 
    Args:
        period: 期數
        total_period: 總期數
        period_type: 包管/代管/轉租
    Returns:
        True/False
        
    """
    if is_int(period) and is_int(total_period):
        period = int(period)
        total_period = int(total_period)
        if period_type == "代管":
            if total_period == 12 and period < total_period : # 1Y
                return True, None, "O"
            else:
                return False, f"Wrong Period: {period} or Total Period {total_period}", "X"
        elif period_type == "包管":
            if total_period == 36 and period < total_period: # 3Y
                return True, None, "O"
            else:
                return False, f"Wrong Period: {period} or Total Period {total_period}", "X"
        elif period_type == "轉租":
            if total_period == 12 and period < total_period: # 1Y
                pass
            # 先不討論這個
            # else:
            return False, f"轉租", "X"
        else:
            return False, f"Wrong Period Type {total_period}", "X"
    
    return False, f"Wrong Period: {period} or Total Period {total_period}", "X"
