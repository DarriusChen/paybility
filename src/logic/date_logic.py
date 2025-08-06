from datetime import datetime
from utils.utils import Result


def valid_dateinfo(id: int, result: Result):
    """檢查轉租約/租賃契約資訊是否正確
    
    Args:
        items:
    Returns:
        dict:
        
    """
    valid_startdate(id, result)
    
    valid_enddate(id, result)



def valid_startdate(id: int, result: Result):
    date = result.get_row("租起日")
    try:
        if '/' not in str(date):
            result.update_substatus("起訖日{id}", False, "錯誤時間格式")
            return None
        
        else:
            parts = date.split('/')
        if len(parts) != 3:
            result.update_substatus("起訖日{id}", False, "錯誤時間格式")
            return None
        
        if len(parts[0]) == 3:
            year = int(parts[0]) + 1911  # 民國轉西元
        else:
            year = int(parts[0]) # 西元年
            
        datetime.strptime(f"{year}/{parts[1]}/{parts[2]}", "%Y/%m/%d")
        result.temp_rowinfo("租起日", f"{year}/{parts[1]}/{parts[2]}")
    except ValueError as e:
        result.update_substatus("起訖日{id}", False, "錯誤時間格式")
        return None
    
def valid_enddate(id: int, result: Result):
    date = result.get_row("租訖日")
    try:
        if '/' not in str(date):
            result.update_substatus("起訖日{id}", False, "錯誤時間格式")
            return None
        
        else:
            parts = date.split('/')
        if len(parts) != 3:
            result.update_substatus("起訖日{id}", False, "錯誤時間格式")
            return None
        
        if len(parts[0]) == 3:
            year = int(parts[0]) + 1911  # 民國轉西元
        else:
            year = int(parts[0]) # 西元年
            
        datetime.strptime(f"{year}/{parts[1]}/{parts[2]}", "%Y/%m/%d")
        result.temp_rowinfo("租訖日", f"{year}/{parts[1]}/{parts[2]}")
    except ValueError as e:
        result.update_substatus("起訖日{id}", False, "錯誤時間格式")
        return None