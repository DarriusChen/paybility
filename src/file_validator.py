import json
import logging
import pandas as pd
import re

from pathlib import Path
from logger import setup_logger, format_func_msg
from utils import MAX_YEAR, MIN_YEAR, PERIOD, COUNTY, TABLES, LOG_PATH, get_dict_template

logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

        
def validate_path(path: str|Path):
    """驗證路徑格式是否正確，並回傳驗證結果。
    
    Args:
        path: 檔案路徑
    Returns:
        dict: 驗證結果
    """
    # abspath
    path = Path(path).resolve()
    
    pathinfo = check_path(path)
    
    fileinfo = check_file(path)
    
    filenameinfo = check_filename(path, fileinfo["sub_status"]["readable"]["info"])
    return pathinfo, fileinfo, filenameinfo
        
def check_path(path: Path):
    """路徑格式檢查
    Args:
        path: 檔案路徑
    Returns:
        dict: 檢查結果
    """
    parts = path.parts
    # print(parts)
    pathinfo = get_dict_template("path_check")
    
    if len(parts) < 5:
        
        # # logger
        # logger.error(format_func_msg(func='check_path',
        #                              msg=f"路徑格式錯誤"))
        # result
        pathinfo["status"]["status"] = False
        pathinfo["status"]["info"] = None
        pathinfo["status"]["message"] = "❌ 路徑格式錯誤"
        
        return pathinfo
    else:
        
        
        for i in range(len(parts)-4):
            # print(parts[i:i+4])
            period, year, county, month = parts[i:i+4]
            
            
            if (re.fullmatch(r"\d+期", period) and
                re.fullmatch(r"\d{3}年", year) and
                re.fullmatch(r".{2}", county) and
                re.fullmatch(r"\d{1,2}月", month)):
               
     
                status, info, message = is_valid_period(period)
                # result
                pathinfo["sub_status"]["period"]["status"] = status
                pathinfo["sub_status"]["period"]["info"] = info
                pathinfo["sub_status"]["period"]["message"] = message
 
       
                status, info, message = is_valid_year(year)
                # result
                pathinfo["sub_status"]["year"]["status"] = status
                pathinfo["sub_status"]["year"]["info"] = info
                pathinfo["sub_status"]["year"]["message"] = message
                    
                status, info, message = is_valid_county(county)
                
                pathinfo["sub_status"]["county"]["status"] = status
                pathinfo["sub_status"]["county"]["info"] = info
                pathinfo["sub_status"]["county"]["message"] = message
                    
                status, info, message = is_valid_month(month)
                pathinfo["sub_status"]["month"]["status"] = status
                pathinfo["sub_status"]["month"]["info"] = info
                pathinfo["sub_status"]["month"]["message"] = message
                
        
        if (pathinfo["sub_status"]["month"]["status"] and pathinfo["sub_status"]["county"]["status"] and
            pathinfo["sub_status"]["year"]["status"] and pathinfo["sub_status"]["period"]["status"]):
            pathinfo["status"]["status"] = True
            pathinfo["status"]["info"] = None
            pathinfo["status"]["message"] = "✅ 路徑格式正確"
            
        return pathinfo
            
def check_file(path: Path):
    """路徑格式檢查
    Args:
        path: 檔案路徑
    Returns:
        dict: 檢查結果
    """
    fileinfo = get_dict_template("file_check")
    

    # suffix check
    status, info, message = is_valid_suffix(path)
    
    fileinfo["sub_status"]["suffix"]["status"] = status
    fileinfo["sub_status"]["suffix"]["info"] = info
    fileinfo["sub_status"]["suffix"]["message"] = message 
    
    status, info, message = is_exist_file(path)
    
    fileinfo["sub_status"]["exist"]["status"] = status
    fileinfo["sub_status"]["exist"]["info"] = info
    fileinfo["sub_status"]["exist"]["message"] = message 
    
    status, info, message = is_readable_file(path)
    
    fileinfo["sub_status"]["readable"]["status"] = status
    fileinfo["sub_status"]["readable"]["info"] = info # 資料中的公司編號
    fileinfo["sub_status"]["readable"]["message"] = message 
    
    if (fileinfo["sub_status"]["readable"]["status"] and 
        fileinfo["sub_status"]["exist"]["status"] and
        fileinfo["sub_status"]["suffix"]["status"]):
        
        fileinfo["status"]["status"] = True
        fileinfo["status"]["info"] = None
        fileinfo["status"]["message"] = "✅ 檔案格式正確"
    else:
        fileinfo["status"]["status"] = False
        fileinfo["status"]["info"] = None
        fileinfo["status"]["message"] = "❌ 檔案格式錯誤"
        
    return fileinfo

def check_filename(path: str, companycode: str):
    """檔名格式檢查
    Args:
        path: 檔案路徑
        companycode: 公司名稱/代號
    Returns:
        dict: 檢查結果
    """
    filenameinfo = get_dict_template("filename_check")
    status, info, message = is_vaild_table(path.name)
    
    filenameinfo["sub_status"]["table"]["status"] = status
    filenameinfo["sub_status"]["table"]["info"] = info
    filenameinfo["sub_status"]["table"]["message"] = message 
    status, info, message =is_same_companycode(path.name, companycode)
    
    filenameinfo["sub_status"]["companycode"]["status"] = status
    filenameinfo["sub_status"]["companycode"]["info"] = info
    filenameinfo["sub_status"]["companycode"]["message"] = message 
    
    if (filenameinfo["sub_status"]["companycode"]["status"] and filenameinfo["sub_status"]["table"]["status"]):
        filenameinfo["status"]["status"] = True
        filenameinfo["status"]["info"] = path.name
        filenameinfo["status"]["message"] = "✅ 檔案名稱正確"
    else:
        filenameinfo["status"]["status"] = False
        filenameinfo["status"]["info"] = path.name
        filenameinfo["status"]["message"] = "❌ 檔案名稱錯誤 須包含表單及公司代號"
        
    return filenameinfo
    
def is_vaild_table(name):
    for t in TABLES:
        if t in name:
            return True, t, "✅ 表單正確"
    return False, None, "❌ 表單錯誤"

def is_same_companycode(filename, companycode):
    if companycode in filename:
        return True, companycode, "✅ 公司名稱/代號相符"
    else:
        return False, None, "❌ 公司名稱/代號不符"
    
def is_valid_suffix(file: Path):
    if file.suffix in [".xlsx", ".xls"]:
        return True, file.suffix, "✅ 副檔名正確"
    else:
        return False, file.suffix, "❌ 副檔名錯誤"

def is_exist_file(file: Path):
    
    if file.exists():
        return True, None, "✅ 檔案存在"
    else:
        return False, None, "❌ 檔案不存在"
    
def is_readable_file(file: Path):
    try:
        df = pd.read_excel(file, header=None) 
        return True, df.iloc[1][2], "✅ 讀取成功"
    except FileNotFoundError as e:
        return False, None, f"❌ 檔案不存在: {e}"
    except Exception as e:
        return False, None, f"❌ 讀取失敗: {e}"
    
def is_valid_period(period: str):
    # period check
    if period[:-1] in PERIOD:    
        return True, period[:-1], "✅ 期別正確"
    else:
        return False, None, "❌ 期別錯誤"

def is_valid_year(year):
    # year check
    if is_int(year[:-1]):
        if MIN_YEAR <= int(year[:-1]) <= MAX_YEAR:
            # 
            return True, int(year[:-1]), "✅ 年限正確"
        else:
            return False, None, "❌年限錯誤"
    else:
        return False, None, "❌年限須為羅馬數字"
    
def is_valid_county(county):
    # county check
    if county in COUNTY:
        return True, county, "✅ 縣市正確"
    else :

        return False, None, "❌ 縣市錯誤"
    
def is_valid_month(month):
    # month check
    
    if is_int(month[:-1]):
        if 1 <= int(month[:-1]) <= 12:          
            return True, int(month[:-1]), "✅ 月份正確" 
        else:
            return False, None, "❌ 月份錯誤"
    else:
        return False, None, "❌ 月份須為羅馬數字"
        
def is_int(s):
    try:
        int(s)
        return True
    except ValueError as e:
        return False