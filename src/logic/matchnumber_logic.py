from pathlib import Path
import logging
import re
from utils.utils import get_dict_template

county_code_dict = {
    "台北市": "A",
    "新北市": "B",
    "桃園市": "C",
    "台中市": "D",
    "台南市": "E",
    "高雄市": "F",
}
# TODO: 縣市代碼資料庫
version_dict = {
    "1": "縣市版",
    "2": "公會版" 
}

numbertype_dict = {
    "M": "媒合編號",
    "T": "房客編號",
    "H": "物件編號"
}

contract_dict = {
    "1": "代租",
    "2": "轉租",
    "3": "包租"
}

def valid_matching_number(matching_code: str, phase: str) -> dict:
    """
    驗證媒合編號是否符合格式。
    
    Args:
        matching_code: 媒合編號
        phase: 計畫期別
    Returns:
        dict
    """

    result = get_dict_template("matchnumber_check")
    
    pattern = r"^([\u4e00-\u9fff]{1,4})([A-F]{1})([12])(M)([123])(2|3|31|4|41)(\d{5})$"
    match = re.match(pattern, matching_code)

    if match:
        result["status"]["status"] = True
        result["status"]["info"] = None
        result["status"]["message"] = "✅ 格式正確"
    else:
        result["status"]["status"] = False
        result["status"]["info"] = None
        result["status"]["message"] = "❌ 格式錯誤"

        # 詳細檢查每個部分
        # 1. 檢查業者名稱（1-4個中文字）--> id_company
        dealer_pattern = r"^([\u4e00-\u9fff]{1,4})"
        dealer_match = re.match(dealer_pattern, matching_code)
        
        if not dealer_match:
            # errors.append(f"業者名稱格式錯誤: {matching_code}。業者名稱須為1~4個中文字")
            result["sub_status"]["matching_code"]["status"] = False
            result["sub_status"]["matching_code"]["info"] = matching_code
            result["sub_status"]["matching_code"]["message"] = "❌ 業者名稱格式錯誤"
        else:
            result["sub_status"]["matching_code"]["status"] = True
            result["sub_status"]["matching_code"]["info"] = matching_code
            result["sub_status"]["matching_code"]["message"] = "✅ 業者名稱格式正確"

        dealer_name = dealer_match.group(1)
        remaining = matching_code[len(dealer_name):]

        status, info, message = is_county(remaining)
        result["sub_status"]["county"]["status"] = status
        result["sub_status"]["county"]["info"] = info
        result["sub_status"]["county"]["message"] = message
        if info =="break":
            return result
        remaining = remaining[1:]

        status, info, message = is_version(remaining)
        result["sub_status"]["version"]["status"] = status
        result["sub_status"]["version"]["info"] = info
        result["sub_status"]["version"]["message"] = message
        if info =="break":
            return result
        remaining = remaining[1:]

        status, info, message = is_numbertype(remaining)
        result["sub_status"]["numbertype"]["status"] = status
        result["sub_status"]["numbertype"]["info"] = info
        result["sub_status"]["numbertype"]["message"] = message
        if info =="break":
            return result
        remaining = remaining[1:]

        status, info, message = is_contract(remaining)
        result["sub_status"]["contract"]["status"] = status
        result["sub_status"]["contract"]["info"] = info
        result["sub_status"]["contract"]["message"] = message
        if info =="break":
            return result
        remaining = remaining[1:]

        status, info, message = is_periodtype(remaining, phase)
        result["sub_status"]["periodtype"]["status"] = status
        result["sub_status"]["periodtype"]["info"] = info
        result["sub_status"]["periodtype"]["message"] = message
        if info =="break":
            return result
        remaining = remaining[1:]

        status, info, message = is_serial_number(remaining)
        result["sub_status"]["serial_number"]["status"] = status
        result["sub_status"]["serial_number"]["info"] = info
        result["sub_status"]["serial_number"]["message"] = message
       
    return result

def is_county(remaining):
    # 2. 檢查縣市代號（A-F）
    if len(remaining) == 0:
        # errors.append("縣市代碼開始出現缺漏！請檢媒合編號是否正確")
        return False, "break", "❌ 縣市代碼開始出現缺漏！請檢媒合編號是否正確"
    elif remaining[0] not in county_code_dict.values():
        # errors.append(f"縣市代號缺漏或格式錯誤: {remaining[0]}。縣市代號須為 A-F")
        return False, None, f"❌ 縣市代號缺漏或格式錯誤: {remaining[0]}。縣市代號須為 A-F"
    elif len(remaining) > 11 or len(remaining) < 10:
        # errors.append(f"縣市代碼後長度不符: {remaining}！請檢查媒合編號是否正確")
        return False, None, f"❌ 縣市代碼後長度不符: {remaining}！請檢查媒合編號是否正確"
    else:
        return True, county_code_dict[remaining[0]], "✅ 縣市代碼正確"
        # remaining = remaining[1:]

def is_version(remaining):
    # 3. 檢查縣市/公會版（1或2）
    
    if len(remaining) == 0:
        # errors.append("縣市版／公會版代碼開始出現缺漏！請檢媒合編號是否正確")
        return False, "break", "❌ 縣市版／公會版代碼開始出現缺漏！請檢媒合編號是否正確"
    elif remaining[0] not in '12':
        # errors.append(f"縣市版或公會版代碼缺漏或格式錯誤: {remaining[0]}。縣市版或公會版代碼須為1或2")
        return False, None, f"❌ 縣市版或公會版代碼缺漏或格式錯誤: {remaining[0]}。縣市版或公會版代碼須為1或2"
    elif len(remaining) > 10 or len(remaining) < 9:
        # errors.append(f"縣市版或公會版代碼後長度不符: {remaining}！請檢查媒合編號是否正確")
        return False, None, f"❌ 縣市版或公會版代碼後長度不符: {remaining}！請檢查媒合編號是否正確"
    else:
        return False, version_dict[remaining[0]], f"✅ 縣市版／公會版代碼正確"
        # remaining = remaining[1:]

def is_numbertype(remaining):
    #  4. 檢查媒合編號類型（M）numbertype
    if len(remaining) == 0:
        # errors.append("媒合編號類型開始出現缺漏！請檢媒合編號是否正確")
        return False, "break", "❌ 媒合編號類型開始出現缺漏！請檢媒合編號是否正確"
    elif remaining[0] != 'M' or 'M' not in remaining:
        # errors.append(f"媒合編號類型缺漏或格式錯誤: {remaining[0]}。媒合編號類型須為大寫M")
        return False, None, f"❌ 媒合編號類型缺漏或格式錯誤: {remaining[0]}。媒合編號類型須為大寫M"
    elif len(remaining) > 9 or len(remaining) < 8:
        # errors.append(f"媒合編號後長度不符: {remaining}！請檢查媒合編號是否正確")
        return False, None, f"❌ 媒合編號後長度不符: {remaining}！請檢查媒合編號是否正確"
    else:
        # remaining = remaining[1:]
        return True, numbertype_dict[remaining[0]], f"✅ 媒合編號正確"

def is_contract(remaining):
    # 5. 檢查契約類型（1、2或3）
    if len(remaining) == 0:
        # errors.append("契約類型開始出現缺漏！請檢媒合編號是否正確")
        return False, "break", "❌ 契約類型開始出現缺漏！請檢媒合編號是否正確"
        
    elif remaining[0] not in '123':
        # errors.append(f"契約類型缺漏或格式錯誤: {remaining[0]}。契約類型須為1、2或3")
        return False, None, f"❌ 契約類型缺漏或格式錯誤: {remaining[0]}。契約類型須為1、2或3"
    elif len(remaining) > 8 or len(remaining) < 7:
        # errors.append(f"契約類型後長度不符: {remaining}！請檢查媒合編號是否正確")
        return False, None, f"❌ 契約類型後長度不符: {remaining}！請檢查媒合編號是否正確"
    else:
        # remaining = remaining[1:]
        return True, contract_dict[remaining[0]], f"✅ 契約類型正確"

def is_periodtype(remaining, phase):
    # 6. 檢查計畫期別（2、3、31、4、41）
    if len(remaining) == 0:
        # errors.append("計畫期別開始出現缺漏！請檢媒合編號是否正確")
        return False, "break", "❌ 計畫期別開始出現缺漏！請檢媒合編號是否正確"
    elif remaining[:len(phase)] != phase:
        # errors.append(f"計畫期別缺漏或格式錯誤: {remaining[:len(phase)]}。計畫期別須為{phase}")
        return False, None, f"❌ 計畫期別缺漏或格式錯誤: {remaining[:len(phase)]}。計畫期別須為{phase}"
    elif len(remaining) > 5 or len(remaining) < 5:
        # errors.append(f"計畫期別後長度不符: {remaining}！請檢查媒合編號是否正確")
        return False, None, f"❌ 計畫期別後長度不符: {remaining}！請檢查媒合編號是否正確"
    else:
        # remaining = remaining[len(phase):]
        return True, phase, "✅ 計畫期別正確"

def is_serial_number(remaining):
    # 7. 檢查流水號（5位數字）
    serial_pattern = r"^(\d{5})$"
    serial_match = re.match(serial_pattern, remaining)
    if not serial_match:
        if len(remaining) == 0:
            # errors.append("流水號缺漏")
            # return False, None, errors
            message = "❌ 流水號缺漏"
        elif len(remaining) > 5 or len(remaining) < 5:
            # errors.append(f"流水號長度不符(應為5位數字): {remaining}！請檢查媒合編號是否正確")
            message = f"❌ 流水號長度不符(應為5位數字): {remaining}！請檢查媒合編號是否正確"
        else:
            # errors.append(f"流水號格式錯誤(應為5位數字): {remaining}！請檢查媒合編號是否正確")
            message = f"❌ 流水號格式錯誤(應為5位數字): {remaining}！請檢查媒合編號是否正確"

        return False, None, message
    else:
        return True, remaining, "✅ 流水號格式正確"
