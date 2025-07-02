from utils.utils import is_int

def sql_basicinfo():
    pass

def sql_historyinfo():
    pass

# insurance_fee: 保險費
# notarization_fee: 公證費
# repair_fee: 修繕費 
# rental_fee: 租金補助 
# development_fee: 開發費
# management_fee: 包管費
# matching_fee: 媒合費
# custody_fee: 代管費

# 包租/轉租/代管期別邏輯

def check_period(period: str, total_period: str, period_type: str):
    
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
        if period_type == "1":
            if total_period == 12 and period < total_period : # 1Y
                return True, None, "O"
            else:
                return False, f"Wrong Period: {period} or Total Period {total_period}", "X"
        elif period_type == "2":
            if total_period == 36 and period < total_period: # 3Y
                return True, None, "O"
            else:
                return False, f"Wrong Period: {period} or Total Period {total_period}", "X"
        elif period_type == "3":
            if total_period == 12 and period < total_period: # 1Y
                pass
            # 先不討論這個
            # else:
            return False, f"轉租", "X"
        else:
            return False, f"Wrong Period Type {total_period}", "X"
    
    return False, f"Wrong Period: {period} or Total Period {total_period}", "X"

def limit_amount(fee: str, history_fee: str, limit: int, cashtype: str):
    if is_int(fee):
        fee = int(fee)

    if is_int(history_fee):
        history_fee = int(history_fee)

    if limit - history_fee <= fee:
        return True, None, f"{cashtype}申請金額符合額度"
    else:
        return False, None, f"{cashtype}申請金額超出額度"

def validate_insurance_fee(fee: str, id: str):
    # 保險費

    # history_fee = get_historyinsurance_fee(id)
    history_fee = 0
    result = limit_amount(fee, history_fee, 3500, "保險費")
   
    return result

def validate_notarization_fee(fee: str, id: str, county_code: str):
    # 公證費
    
    
    # history_fee = get_historynotarization_fee(id)
    history_fee = 0

    if county_code in "AB":
        # 雙北
        result = limit_amount(fee, history_fee, 4500, "公證費")
    else:
        result = limit_amount(fee, history_fee, 3000, "公證費")


    return result

def validate_repair_fee(id: str,  fee: str, contract: str):
    # 修繕費 

    # history_fee1 = get_historyrepair_fee_fee(id) 過去修繕費
    history_fee1 = 0
    
    if contract == 1:
        # 代租代管
        # history_fee2 = get_historyinsurance_fee_fee(id) 過去保險費
        history_fee2 = 0
        if 3500 - history_fee2 >= 0:
            result = limit_amount(fee, history_fee1, 6500 + (3500 - history_fee2), "修繕費")
        else:
            return False, 3500 - history_fee2, f"代租 修繕費異常"
    else:
        result = limit_amount(fee, history_fee1, 10000, "修繕費")

    return result

def validate_rental_fee(id: str, fee: str, rental_period="", rental_totalperiod="", rental_type=""):
    # 租金補助 

    
    if int(fee):
        fee = int(fee)
        if fee != 0:
            return False, None, f"租金補助異常"
        else:
            return True, None, f"無租金補助"
    else:
        return True, None, f"租金補助金額異常"

def validate_development_fee(fee: str, id: str, county_code: str):
    # 開發費

    # history_fee = get_historydevelopment_fee_fee(id)
    history_fee = 0
    if county_code == "A": #台北
        result = limit_amount(fee, history_fee, 24000, "開發費")
    elif county_code == "B": #新北
        result = limit_amount(fee, history_fee, 22000, "開發費")
    elif county_code in "CD": #桃園、台中
        result = limit_amount(fee, history_fee, 18000, "開發費")
    elif county_code == "EF": #台南、高雄
        result = limit_amount(fee, history_fee, 16000, "開發費")
    else:
        return False, None, "縣市代碼錯誤"
    
    return result

def validate_management_fee(fee: str, id: str, county_code: str, period_type: str, period:str, total_period:str):
    # 包管費

    history_fee = 0
    if county_code == "A": #台北
        result = limit_amount(fee, history_fee, 4000, "包管費")
    elif county_code == "B": #新北
        result = limit_amount(fee, history_fee, 3600, "包管費")
    elif county_code in "CD": #桃園、台中
        result = limit_amount(fee, history_fee, 3000, "包管費")
    elif county_code == "EF": #台南、高雄
        result = limit_amount(fee, history_fee, 2600, "包管費")
    else:
        return False, None, "縣市代碼錯誤"
    
    return result

def validate_matching_fee(fee: str, id: str, county_code: str):
    # 媒合費
    history_fee = 0
    if county_code == "A": #台北
        result = limit_amount(fee, history_fee, 16000, "媒合費")
    elif county_code == "B": #新北
        result = limit_amount(fee, history_fee, 14000, "媒合費")
    elif county_code in "CD": #桃園、台中
        result = limit_amount(fee, history_fee, 13000, "媒合費")
    elif county_code == "EF": #台南、高雄
        result = limit_amount(fee, history_fee, 11000, "媒合費")
    else:
        return False, None, "縣市代碼錯誤"
    
    return result

def validate_custody_fee(fee: str, id: str, county_code: str):
    # 代管費
    history_fee = 0
    if county_code == "A": #台北
        result = limit_amount(fee, history_fee, 2400, "代管費")
    elif county_code == "B": #新北
        result = limit_amount(fee, history_fee, 2200, "代管費")
    elif county_code in "CD": #桃園、台中
        result = limit_amount(fee, history_fee, 1800, "代管費")
    elif county_code == "EF": #台南、高雄
        result = limit_amount(fee, history_fee, 1500, "代管費")
    else:
        return False, None, "縣市代碼錯誤"
    
    return result