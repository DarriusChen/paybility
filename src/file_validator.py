
import pandas as pd
import re

from pathlib import Path
from logger import setup_logger, format_func_msg
from utils.utils import MAX_YEAR, MIN_YEAR, PERIOD, COUNTY, MAPPING_FILE, TABLES, LOG_PATH, get_dict_template, is_int, load_data

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
    
    fileinfo = get_dict_template("file_check")

    # name
    status, info, message = check_name(path)

    fileinfo["sub_status"]["name"]["status"] = status
    fileinfo["sub_status"]["name"]["info"] = info # 檔案名稱中的業者編號
    fileinfo["sub_status"]["name"]["message"] = message 

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
    print(type(info), info)
    fileinfo["sub_status"]["readable"]["status"] = status
    fileinfo["sub_status"]["readable"]["info"] = info # 單個表的dataframe
    fileinfo["sub_status"]["readable"]["message"] = message 

    company_code = fileinfo["sub_status"]["name"]["info"]['B']
    status, info, message = is_valid_company(company_code)
 
    fileinfo["sub_status"]["company_info"]["status"] = status
    fileinfo["sub_status"]["company_info"]["info"] = info # 資料中的 '縣市' '縣市代碼' '業者名稱' '系統業者代號'
    fileinfo["sub_status"]["company_info"]["message"] = message 
    
    if (fileinfo["sub_status"]["name"]["status"] and
        fileinfo["sub_status"]["readable"]["status"] and 
        fileinfo["sub_status"]["exist"]["status"] and
        fileinfo["sub_status"]["suffix"]["status"] and 
        fileinfo["sub_status"]["company_info"]["status"]):
        
        fileinfo["status"]["status"] = True
        fileinfo["status"]["info"] = None
        fileinfo["status"]["message"] = "✅ 檔案格式正確"
    else:
        fileinfo["status"]["status"] = False
        fileinfo["status"]["info"] = None
        fileinfo["status"]["message"] = "❌ 檔案格式錯誤"
    
    return fileinfo
        
    
def check_name(path):
    
    result = {}
    errors = []
    # A：表4_、表7_、表9_
    match_a = re.match(r"^表(4|7|9)_", path.name)
    if not match_a:
        errors.append("A：應為表4_、表7_ 或 表9_")
    else:
        result["A"] = "表"+match_a.group(1)

    # B（2~4個中文字）
    match_b = re.search(r"^表(4|7|9)_([\u4e00-\u9fff]{2,4})", path.name)
    if not match_b:
        errors.append("B：應為2到4個中文字（地區名稱)")
    else:
        result["B"] = match_b.group(2)

    # C（期別）
    match_c = re.search(r"([\u4e00-\u9fff]{2,4})(1|2|3|31|4|41)期", path.name)
    if not match_c:
        errors.append("C：期數應為 1、2、3、31、4 或 41，並以「期」結尾")
    else:
        result["C"] = match_c.group(2)

    # D（對象）
    match_d = re.search(r"(出租人|承租人|業者服務)補助費用清冊", path.name)
    if not match_d:
        errors.append("D：對象應為 出租人 / 承租人 / 業者")
    else:
        result["D"] = match_d.group(1)

    # E（民國年）
    match_e = re.search(r"補助費用清冊_(1\d{2})", path.name)
    if not match_e:
        errors.append("E：應為民國年份")
    else:
        result["E"] = match_e.group(1)
    # F（月）
    match_f = re.search(r"補助費用清冊_(1\d{2})(0[1-9]|1[0-2])", path.name)
    if not match_f:
        errors.append("F：月份應為 01~12")
    else:
        result["F"] = match_f.group(2)

    if errors == []:
        return True, result, "✅ 檔名格式正確"
    else:
        errors = ["❌ 表[A]_[B][C]期[D]補助費用清冊_[E][F]"] + errors

        return False, result, "\n".join(errors)
    
def is_valid_company(name_code = ""):
    
    mapping_df = pd.read_excel(MAPPING_FILE,
                        sheet_name="4-1",
                        header=0)
    # mapping_df[['縣市', '縣市代碼']] = mapping_df[['縣市', '縣市代碼']].ffill()
    mapping_df.loc[:, ['縣市', '縣市代碼', '業者名稱', '系統業者代號']] = mapping_df.loc[:, ['縣市', '縣市代碼', '業者名稱', '系統業者代號']].ffill()
    
    result = mapping_df[mapping_df['系統業者代號']==name_code]
    
    if not result.empty:
        result = result.iloc[0].to_dict()
        return True, result, f"✅ 系統業者代號相符: {result['系統業者代號']}"
    else:
        return False, None, f"❌ 系統業者代號相異"

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
        
        return True, df.values.tolist(), "讀取成功"
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
        
