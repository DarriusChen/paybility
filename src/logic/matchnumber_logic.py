import re
from utils.utils import Result

county_code_dict = {
    "台北市": "A",
    "新北市": "B",
    "桃園市": "C",
    "台中市": "D",
    "台南市": "E",
    "高雄市": "F",
}

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

def valid_matching_number(result: Result) -> dict:
    """
    """
    matching_code =  result.get_row("媒合編號")

    company_name_ = result.get_info("業者代碼")
    county_code_ = result.get_info("縣市代碼")
    period_type_ = result.get_info("期別")

    pattern = rf"^({company_name_})({county_code_})([12])(M)([123])({period_type_})(\d{{5}})$"
    match = re.match(pattern, matching_code)
    if match:
        company_name, county_code, version, numbertype, contract, period_type, serial_number = match.groups()
        result.insert_rowinfo("媒合編號", matching_code)
        result.insert_rowinfo("業者代碼", company_name)
        result.insert_rowinfo("縣市代碼", county_code)
        result.insert_rowinfo("版本", version)
        result.insert_rowinfo("編號類型", numbertype)
        result.insert_rowinfo("契約類型", contract)
        result.insert_rowinfo("期別", period_type)
        result.insert_rowinfo("流水號", serial_number)

        
    else:
        # 詳細檢查每個部分
        
        _, num = is_matchnumber(matching_code, result)
        if not _:
            return None
        else:
            remaining = matching_code[num:]

        _ = is_county(remaining, result) 
        if not _:
            return None
        else:
            remaining = remaining[1:]

        _ = is_version(remaining, result)
        if not _:
            return None
        else:
            remaining = remaining[1:]

        _ = is_numbertype(remaining, result)
        if not _:
            return None
        else:
            remaining = remaining[1:]

        _ = is_contract(remaining, result)
        if not _:
            return None
        else:
            remaining = remaining[1:]

        _ = is_periodtype(remaining, result)
        if not _:
            return None
        else:
            remaining = remaining[1:]

        _ = is_serial_number(remaining, result)
        if not _:
            return None
        else:
            remaining = remaining[1:]

    # result.insert_rowinfo("媒合編號", matching_code)
    


def is_matchnumber(remaining, result: Result):
    # 1. 檢查業者名稱（1-4個中文字）--> id_company
    company_name = result.get_info("業者代碼")
    dealer_match = re.match(company_name, remaining)

    if not dealer_match:
        result.insert_rowerror(f"媒合編號", f"業者名稱錯誤: {remaining}")
        return False, 0
    else:
        dealer_name = dealer_match.group(0)
        result.insert_rowinfo("業者代碼", dealer_name)
        return True, len(dealer_name)

def is_county(remaining, result: Result):
    company_code = result.get_info("縣市代碼")
    # 2. 檢查縣市代號（A-F）
    if len(remaining) == 0:
        result.insert_rowerror(f"媒合編號", "縣市代碼開始出現缺漏！請檢媒合編號是否正確")
        return False
    elif remaining[0] != company_code:
        result.insert_rowerror(f"媒合編號", f"縣市代號錯誤: {remaining[0]}。縣市代號須為 A-F")
        return False
    elif len(remaining) > 11 or len(remaining) < 10:
        result.insert_rowerror(f"媒合編號", f"縣市代碼後長度不符: {remaining}！請檢查媒合編號是否正確")
        return False
    else:
        result.insert_rowinfo("縣市代碼", county_code_dict[remaining[0]])
        return True

def is_version(remaining, result: Result):
    # 3. 檢查縣市/公會版（1或2）
    
    if len(remaining) == 0:
        # errors.append("縣市版／公會版代碼開始出現缺漏！請檢媒合編號是否正確")
        result.insert_rowerror(f"媒合編號", "縣市版／公會版代碼開始出現缺漏！請檢媒合編號是否正確")
        return False
    elif remaining[0] not in '12':
        result.insert_rowerror(f"媒合編號", f"縣市版或公會版代碼缺漏或格式錯誤: {remaining[0]}。縣市版或公會版代碼須為1或2")
        return False
    elif len(remaining) > 10 or len(remaining) < 9:
        result.insert_rowerror(f"媒合編號", f"縣市版或公會版代碼後長度不符: {remaining}！請檢查媒合編號是否正確")
        return False
    else:
        result.insert_rowinfo("版本", version_dict[remaining[0]])
        return True

def is_numbertype(remaining, result: Result):
    #  4. 檢查媒合編號類型（M）numbertype
    if len(remaining) == 0:
        result.insert_rowerror(f"媒合編號", "編號類型開始出現缺漏！請檢媒合編號是否正確")
        return False
    elif remaining[0] != 'M' or 'M' not in remaining:
        result.insert_rowerror(f"媒合編號", f"編號類型缺漏或格式錯誤: {remaining[0]}。媒合編號類型須為大寫M")
        return False
    elif len(remaining) > 9 or len(remaining) < 8:
        result.insert_rowerror(f"媒合編號", f"編號類型後長度不符: {remaining}！請檢查媒合編號是否正確")
        # errors.append(f"媒合編號後長度不符: {remaining}！請檢查媒合編號是否正確")
        return False
    else:
        result.insert_rowinfo("編號類型", numbertype_dict[remaining[0]])
        return True

def is_contract(remaining, result: Result):
    # 5. 檢查契約類型（1、2或3）
    if len(remaining) == 0:
        result.insert_rowerror(f"媒合編號", "契約類型開始出現缺漏！請檢媒合編號是否正確")
        return False
    elif remaining[0] not in '123':
        result.insert_rowerror(f"媒合編號", f"契約類型缺漏或格式錯誤: {remaining[0]}。契約類型須為1、2或3")
        return False
    elif len(remaining) > 8 or len(remaining) < 7:
        result.insert_rowerror(f"媒合編號", f"契約類型後長度不符: {remaining}！請檢查媒合編號是否正確")
        return False
    else:
        result.insert_rowinfo("契約類型", contract_dict[remaining[0]])
        return True

def is_periodtype(remaining, result: Result):
    # 6. 檢查計畫期別（2、3、31、4、41）
    phase = result.get_info("期別")
    if len(remaining) == 0:
        result.insert_rowerror(f"媒合編號", "計畫期別開始出現缺漏！請檢媒合編號是否正確")
        return False
    elif remaining[:len(phase)] != phase:
        result.insert_rowerror(f"媒合編號", f"計畫期別缺漏或格式錯誤: {remaining[:len(phase)]}。計畫期別須為{phase}")
        return False 
    elif len(remaining) > 5 or len(remaining) < 5:
        result.insert_rowerror(f"媒合編號", f"計畫期別後長度不符: {remaining}！請檢查媒合編號是否正確")
        return False
    else:
        result.insert_rowinfo("期別", phase)
        return True

def is_serial_number(remaining, result: Result):
    # 7. 檢查流水號（5位數字）
    serial_pattern = r"^(\d{5})$"
    serial_match = re.match(serial_pattern, remaining)
    if not serial_match:
        if len(remaining) == 0:
            # errors.append("流水號缺漏")
            # return False, None, errors
            result.insert_rowerror("媒合編號", "流水號缺漏")
            return False
        elif len(remaining) > 5 or len(remaining) < 5:
            result.insert_rowerror("媒合編號", f"流水號長度不符(應為5位數字): {remaining}！請檢查媒合編號是否正確")
            return False
        else:
            result.insert_rowerror("媒合編號", f"流水號格式錯誤(應為5位數字): {remaining}！請檢查媒合編號是否正確")
            return False

    else:
        result.insert_rowinfo("流水號", remaining)
        return True
