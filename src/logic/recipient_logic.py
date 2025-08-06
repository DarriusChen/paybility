import re
from utils.utils import is_int, Result
# 申請人/受款人檢查邏輯


def valid_recipientinfo(result: Result):
    """檢查受款人資訊是否正確
    
    Args:
        items: dict
        result: dict{}
    Returns:
        result: dict{}
        
    """
    # result = get_dict_template("recipient_check")

    # print(name, name_id, bank_id, branch_id, account)
    is_name_valid(result)

    check_ID(result)

    is_bank_vaild(result)

    is_branch_vaild(result)

    is_account_vaild(result)

    
# name check 
def is_name_valid(result: Result):

    name = result.get_row("姓名")
    if not isinstance(name, str):   
        result.insert_rowerror(f"受款人", "名字無效")
    else:
        result.insert_rowinfo("姓名", name)
        

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
    
def check_ID(result: Result):

    name_id = result.get_row("身分證")
    # print(f"ID: ")
    if isinstance(name_id, str):   
        if is_idformat_valid(name_id):
            letter = str(name_id[0]).upper()
            number = name_id[1:]
            
            code = get_letter_digits(letter)
            code += number
            weight = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1, 1]
            
            total = 0
            for c, w in zip(code, weight):
                total += int(c) * int(w)
            
            if total % 10 == 0:
                result.insert_rowinfo("身分證", name_id)
                return None
            else:
                result.insert_rowerror(f"受款人", "身分證未通過檢查碼")
                return None
        else:
            result.insert_rowerror(f"受款人", "身分證格式錯誤")
            return None
    else:
        result.insert_rowerror(f"受款人", "身分證型別錯誤")
        return None

def is_bank_vaild(result: Result):
    code = result.get_row("銀行代碼")
    code = str(is_int(code))
    if code:
        if len(code) <= 3:
            if len(code) == 2:
                code = "0" + code
            elif len(code) == 1:
                code = "00" + code
        
            result.insert_rowinfo("銀行代碼", code)
        else:
            result.insert_rowerror(f"受款人", "銀行代碼長度錯誤")
    else:
        result.insert_rowerror(f"受款人", "銀行代碼錯誤")
        return None
    
def is_branch_vaild(result: Result):
    code = result.get_row("分行代碼")
    code = str(is_int(code))
    if code:
        if len(code) == 4:
            result.insert_rowinfo("分行代碼", code)
            return None
        else:
            result.insert_rowerror(f"受款人", "分行代碼長度錯誤")
    else:
        result.insert_rowerror(f"受款人", "分行代碼錯誤")
        return None
    
def is_account_vaild(result: Result):
    code = result.get_row("帳號")
    code = str(is_int(code))
    if code:
        if len(code) <= 18:
            # padding to length 18
            code = "0" * (18 - len(code)) + code

            result.insert_rowinfo("帳號", code)
            return None
        else:
            result.insert_rowerror(f"受款人", "帳號長度錯誤")
    else:
        result.insert_rowerror(f"受款人", "帳號錯誤")
        return None
    

    