from utils.utils import is_int

from database import DatabaseService

from utils.utils import load_schema, Result

# insurance_cash: 保險費
# notarization_cash: 公證費
# repair_cash: 修繕費 
# rental_cash: 租金補助 
# development_cash: 開發費
# management_cash: 包管費
# matching_cash: 媒合費
# custody_cash: 代管費


class CashDatabase(DatabaseService):
    def __init__(self, file_type:str, number:str):
        super().__init__()

        if file_type == "表4":
            self.file_type = "表4"
            self.sql_type = "ContractHouse_PayTable_0205_sheet_4_plan41"
        elif file_type == "表7":
            self.file_type = "表7"
            self.sql_type = "ContractHouse_PayTable_0205_sheet_7_plan41"
        elif file_type == "表9":
            self.file_type = "表9"
            self.sql_type = "ContractHouse_PayTable_0205_sheet_9_plan41"
        elif file_type == "GS400":
            self.file_type = "GS400"
            self.sql_type = "ContractHouse_GS400"

        self.number = number
        self.results = super().get_data_by_match_id(self.number, self.sql_type)
        self.sqlname_map = self.get_sqlname_map()

    def get_history_cash(self, cash_type:str):
        history_cash = 0
        
        for result in self.results:
            if isinstance(result, dict):
                history_cash += int(result[self.sqlname_map[cash_type]])

        return history_cash

    def get_sqlname_map(self):
        if self.file_type == "表4":
            sql_dict = {
                "保險費": "居家安全保險費申請金額",
                "公證費": "公證費申請金額",
                "修繕費": "住宅出租修繕費申請金額"
            }
        elif self.file_type == "表7":
            sql_dict = {
                "公證費": "公證費申請金額",
                "租金補助": "租金補助申請金額"
            }
        elif self.file_type == "表9":
            sql_dict = {
                "公證費": "公證費申請金額",
                "開發費": "開發費申請金額",
                "包管費": "包管費申請金額",
                "媒合費": "媒合費申請金額",
                "代管費": "代管費申請金額"
            }
        else:
            sql_dict = {}
        return sql_dict

    
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
                return True, None, "期別正確"
            else:
                return False, None, f"期別錯誤: {period}/{total_period}"
        elif period_type == "2":
            if total_period == 36 and period < total_period: # 3Y
                return True, None, "期別正確"
            else:
                return False, None, f"期別錯誤: {period}/{total_period}"
        elif period_type == "3":
            if total_period == 12 and period < total_period: # 1Y
                pass
            # 先不討論這個
            # else:
            return False, f"轉租", "目前沒有轉租偵錯功能"
        else:
            return False, None, f"類別錯誤 {period_type}"
    
    return False, None, f"期別錯誤: {period}/{total_period}"

def limit_amount(cash: int, history_cash: int, limit: int):

    if limit - history_cash >= cash:
        return True, None, f"✔ 符合額度   上限:{limit} | 申請: {cash} | 已使用: {history_cash}"
    else:
        return False, None, f"✖ 超出額度   上限:{limit} | 申請: {cash} | 已使用: {history_cash}"

def valid_cash(id: int, result: Result):

    file_type = result.get_info("表種")
    county_code = result.get_info("縣市代碼")
    
    number = result.get_rowinfo("媒合編號")
    contract = result.get_rowinfo("契約類型")
    cash_type = result.get_rowinfo("費用")

    result.update_substatus(f"費用{id}", False, "未檢查")
    return 0
    db = CashDatabase(file_type, number)
    
    history_cash = db.get_history_cash(cash_type)

    if cash_type == "保險費":
        
        cash_result= limit_amount(cash, history_cash, 3500)
    elif cash_type == "公證費":
        if county_code in "AB":
            # 雙北
            cash = limit_amount(cash, history_cash, 4500)
        else:
            cash_result= limit_amount(cash, history_cash, 3000)
    elif cash_type == "修繕費":

        if contract == 1:
            # 代租代管
            history_cash2 = db.get_history_cash("保險費") # 過去保險費
            
            if 3500 - history_cash2 >= 0:
                cash_result= limit_amount(cash, history_cash, 6500 + (3500 - history_cash2), "修繕費")
            else:
                result
                return False, 3500 - history_cash2, f"代租 修繕費異常"
        else:
            cash_result= limit_amount(cash, history_cash, 10000)

    elif cash_type == "租金補助":
        if int(cash):
            cash = int(cash)
            if cash != 0:
                return False, None, f"租金補助異常"
            else:
                return True, None, f"無租金補助"
        else:
            return True, None, f"租金補助金額異常"
    elif cash_type == "開發費":
        if county_code == "A": #台北
            cash_result= limit_amount(cash, history_cash, 24000)
        elif county_code == "B": #新北
            cash_result= limit_amount(cash, history_cash, 22000)
        elif county_code in "CD": #桃園、台中
            cash_result= limit_amount(cash, history_cash, 18000)
        elif county_code == "EF": #台南、高雄
            cash_result= limit_amount(cash, history_cash, 16000)
        else:
            return False, None, "縣市代碼錯誤"
    elif cash_type == "包管費":
        if county_code == "A": #台北
            cash_result= limit_amount(cash, history_cash, 4000)
        elif county_code == "B": #新北
            cash_result= limit_amount(cash, history_cash, 3600)
        elif county_code in "CD": #桃園、台中
            cash_result= limit_amount(cash, history_cash, 3000)
        elif county_code == "EF": #台南、高雄
            cash_result= limit_amount(cash, history_cash, 2600)
        else:
            return False, None, "縣市代碼錯誤"
    elif cash_type == "媒合費":
        if county_code == "A": #台北
            cash_result= limit_amount(cash, history_cash, 16000)
        elif county_code == "B": #新北
            cash_result= limit_amount(cash, history_cash, 14000)
        elif county_code in "CD": #桃園、台中
            cash_result= limit_amount(cash, history_cash, 13000)
        elif county_code == "EF": #台南、高雄
            cash_result= limit_amount(cash, history_cash, 11000)
        else:
            return False, None, "縣市代碼錯誤"
    elif cash_type == "代管費":
        if county_code == "A": #台北
            cash_result= limit_amount(cash, history_cash, 2400)
        elif county_code == "B": #新北
            cash_result= limit_amount(cash, history_cash, 2200)
        elif county_code in "CD": #桃園、台中
            cash_result= limit_amount(cash, history_cash, 1800)
        elif county_code == "EF": #台南、高雄
            cash_result= limit_amount(cash, history_cash, 1500)
        else:
            return False, None, "縣市代碼錯誤"
    else:
        raise Exception("費用類型錯誤")
    
    return result

# --------------------------------
import re
def test_valid_cash(number: str, cash_type:str, cash:str, history_cash: int):


    pattern = rf"^([\u4e00-\u9fff]{{1,4}})(A|B|C|D|E|F)([12])(M)([123])(2|3|31|4|41)(\d{{5}})$"
    match = re.match(pattern, number)
    if not match:
        return "媒合編號有誤"
        
    else:
        company_name, county_code, version, numbertype, contract, period_type, serial_number = match.groups()

        if cash_type == "保險費":
            
            cash_result= limit_amount(cash, history_cash, 3500)
        elif cash_type == "公證費":
            if county_code in "AB":
                # 雙北
                cash_result= limit_amount(cash, history_cash, 4500)
            else:
                cash_result= limit_amount(cash, history_cash, 3000)
        elif cash_type == "修繕費":

            if contract == 1:
                # 代租代管
                # history_cash2 = db.get_history_cash("保險費") # 過去保險費
                history_cash2 = 0
                if 3500 - history_cash2 >= 0:
                    cash_result= limit_amount(cash, history_cash, 10000 - history_cash2)
                else:
                    return f"代租 修繕費異常"
            else:
                cash_result= limit_amount(cash, history_cash, 10000)

        elif cash_type == "租金補助":

            if int(cash) != 0:
                return False, None, f"租金補助異常"
            else:
                return True, None, f"無租金補助"

        elif cash_type == "開發費":
            if county_code == "A": #台北
                cash_result= limit_amount(cash, history_cash, 24000)
            elif county_code == "B": #新北
                cash_result= limit_amount(cash, history_cash, 22000)
            elif county_code in "CD": #桃園、台中
                cash_result= limit_amount(cash, history_cash, 18000)
            elif county_code in "EF": #台南、高雄
                cash_result= limit_amount(cash, history_cash, 16000)
            else:
                return "縣市代碼錯誤"
            
        elif cash_type == "包管費":
            if county_code == "A": #台北
                cash_result= limit_amount(cash, history_cash, 4000)
            elif county_code == "B": #新北
                cash_result= limit_amount(cash, history_cash, 3600)
            elif county_code in "CD": #桃園、台中
                cash_result= limit_amount(cash, history_cash, 3000)
            elif county_code in "EF": #台南、高雄
                cash_result= limit_amount(cash, history_cash, 2600)
            else:
                return "縣市代碼錯誤"
        elif cash_type == "媒合費":
            if county_code == "A": #台北
                cash_result= limit_amount(cash, history_cash, 16000)
            elif county_code == "B": #新北
                cash_result= limit_amount(cash, history_cash, 14000)
            elif county_code in "CD": #桃園、台中
                cash_result= limit_amount(cash, history_cash, 13000)
            elif county_code in "EF": #台南、高雄
                cash_result= limit_amount(cash, history_cash, 11000)
            else:
                return "縣市代碼錯誤"
        elif cash_type == "代管費":
            if county_code == "A": #台北
                cash_result= limit_amount(cash, history_cash, 2400)
            elif county_code == "B": #新北
                cash_result= limit_amount(cash, history_cash, 2200)
            elif county_code in "CD": #桃園、台中
                cash_result= limit_amount(cash, history_cash, 1800)
            elif county_code in "EF": #台南、高雄
                cash_result= limit_amount(cash, history_cash, 1500)
            else:
                return "縣市代碼錯誤"
        else:
            raise "費用類型錯誤"
        
        return result[-1]

# --------------------------------
    
    
def validate_insurance_cash(cash: str, id: str):
    # 保險費

    # history_cash = get_historyinsurance_cash(id)
    history_cash = 0
    cash_result= limit_amount(cash, history_cash, 3500)
   
    return result

def validate_notarization_cash(cash: str, id: str, county_code: str):
    # 公證費
    
    
    # history_cash = get_historynotarization_cash(id)
    history_cash = 0

    if county_code in "AB":
        # 雙北
        cash_result= limit_amount(cash, history_cash, 4500)
    else:
        cash_result= limit_amount(cash, history_cash, 3000)

    return result

def validate_repair_cash(id: str,  cash: str, contract: str):
    # 修繕費 

    # history_cash1 = get_historyrepair_cash_cash(id) 過去修繕費
    history_cash1 = 0
    
    if contract == 1:
        # 代租代管
        # history_cash2 = get_historyinsurance_cash_cash(id) 過去保險費
        history_cash2 = 0
        if 3500 - history_cash2 >= 0:
            cash_result= limit_amount(cash, history_cash1, 6500 + (3500 - history_cash2), "修繕費")
        else:
            return False, 3500 - history_cash2, f"代租 修繕費異常"
    else:
        cash_result= limit_amount(cash, history_cash1, 10000)

    return result

def validate_rental_cash(id: str, cash: str, rental_period="", rental_totalperiod="", rental_type=""):
    # 租金補助 

    
    if int(cash):
        cash = int(cash)
        if cash != 0:
            return False, None, f"租金補助異常"
        else:
            return True, None, f"無租金補助"
    else:
        return True, None, f"租金補助金額異常"

def validate_development_cash(cash: str, id: str, county_code: str):
    # 開發費

    # history_cash = get_historydevelopment_cash_cash(id)
    history_cash = 0
    if county_code == "A": #台北
        cash_result= limit_amount(cash, history_cash, 24000)
    elif county_code == "B": #新北
        cash_result= limit_amount(cash, history_cash, 22000)
    elif county_code in "CD": #桃園、台中
        cash_result= limit_amount(cash, history_cash, 18000)
    elif county_code == "EF": #台南、高雄
        cash_result= limit_amount(cash, history_cash, 16000)
    else:
        return False, None, "縣市代碼錯誤"
    
    return result

def validate_management_cash(cash: str, id: str, county_code: str, period_type: str, period:str, total_period:str):
    # 包管費

    history_cash = 0
    if county_code == "A": #台北
        cash_result= limit_amount(cash, history_cash, 4000)
    elif county_code == "B": #新北
        cash_result= limit_amount(cash, history_cash, 3600)
    elif county_code in "CD": #桃園、台中
        cash_result= limit_amount(cash, history_cash, 3000)
    elif county_code == "EF": #台南、高雄
        cash_result= limit_amount(cash, history_cash, 2600)
    else:
        return False, None, "縣市代碼錯誤"
    
    return result

def validate_matching_cash(cash: str, id: str, county_code: str):
    # 媒合費
    history_cash = 0
    if county_code == "A": #台北
        cash_result= limit_amount(cash, history_cash, 16000)
    elif county_code == "B": #新北
        cash_result= limit_amount(cash, history_cash, 14000)
    elif county_code in "CD": #桃園、台中
        cash_result= limit_amount(cash, history_cash, 13000)
    elif county_code == "EF": #台南、高雄
        cash_result= limit_amount(cash, history_cash, 11000)
    else:
        return False, None, "縣市代碼錯誤"
    
    return result

def validate_custody_cash(cash: str, id: str, county_code: str):
    # 代管費
    history_cash = 0
    if county_code == "A": #台北
        cash_result= limit_amount(cash, history_cash, 2400)
    elif county_code == "B": #新北
        cash_result= limit_amount(cash, history_cash, 2200)
    elif county_code in "CD": #桃園、台中
        cash_result= limit_amount(cash, history_cash, 1800)
    elif county_code == "EF": #台南、高雄
        cash_result= limit_amount(cash, history_cash, 1500)
    else:
        return False, None, "縣市代碼錯誤"
    
    return result
