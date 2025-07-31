
import pandas as pd
import re

from pathlib import Path
from logger import setup_logger, format_func_msg
from utils.utils import MAX_YEAR, MIN_YEAR, PERIOD, COUNTY, MAPPING_FILE, TABLES, LOG_PATH, get_dict_template, is_int,  load_schema

logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

        
def validate_path(file):
    """驗證路徑格式是否正確，並回傳驗證結果。
    
    Args:
        path: 檔案路徑
    Returns:
        dict: 驗證結果
    """
    # abspath
    if isinstance(file, str):
        path = Path(file).resolve()
    else:
        path = Path(file.name).resolve()
    
    fileinfo = get_dict_template("file_check")

    # name
    status, info, message = check_name(path)

    fileinfo["sub_status"]["檔案名稱"]["status"] = status
    fileinfo["sub_status"]["檔案名稱"]["info"] = info # 檔案名稱中的業者編號
    fileinfo["sub_status"]["檔案名稱"]["message"] = message 
    
    status, info, message = is_readable_file(file)

    fileinfo["sub_status"]["讀取"]["status"] = status
    fileinfo["sub_status"]["讀取"]["info"] = info # 單個表的dataframe
    fileinfo["sub_status"]["讀取"]["message"] = message 

    if fileinfo["sub_status"]["檔案名稱"]["info"].get('業者代碼') != None:
        company_code = fileinfo["sub_status"]["檔案名稱"]["info"]['業者代碼']
        status, info, message = is_valid_company(company_code)
 
        fileinfo["sub_status"]["業者代碼"]["status"] = status
        fileinfo["sub_status"]["業者代碼"]["info"] = info # 資料中的 '縣市' '縣市代碼' '業者名稱' '系統業者代號'
        fileinfo["sub_status"]["業者代碼"]["message"] = message 
    
    if (fileinfo["sub_status"]["檔案名稱"]["status"] and
        fileinfo["sub_status"]["讀取"]["status"] and 
        fileinfo["sub_status"]["業者代碼"]["status"]):
        
        fileinfo["status"]["status"] = True
        fileinfo["status"]["info"] = None
        fileinfo["status"]["message"] = "格式正確"
    else:
        fileinfo["status"]["status"] = False
        fileinfo["status"]["info"] = None
        fileinfo["status"]["message"] = "格式錯誤"
    
    return fileinfo
        
    
def check_name(path):
    
    result = {}
    # 表4_、表7_、表9_
    match = re.match(r"^(表4|表7|表9)_", path.name)
    if not match:

        result["業者代碼"] = "未檢查"
        return False, result, "應為表4、表7、表9，並以符號'_'接續"
        # errors.append("應為表4_、表7_ 或 表9_")
    else:
        result["表種"] = match.group(1)

    # 2~4個中文字
    match = re.search(r"^(表4|表7|表9)_([\u4e00-\u9fff]{2,4})", path.name)
    if not match:
        return False, result, "應為2到4個中文字的業者代碼"
        # errors.append("應為2到4個中文字（地區名稱)")
    else:
        result["業者代碼"] = match.group(2)

    # 期別
    match = re.search(r"([\u4e00-\u9fff]{2,4})(1|2|3|31|4|41)期", path.name)
    if not match:
        return False, result, "期數應為 1、2、3、31、4 或 41，並以'期'結尾"
        # errors.append("期數應為 1、2、3、31、4 或 41，並以「期」結尾")
    else:
        result["期別"] = match.group(2)

    # 對象
    match = re.search(r"(出租人|承租人|業者服務)補助費用清冊", path.name)
    if not match:
        return False, result, "對象應為: 出租人、承租人、業者"
        # errors.append("對象應為 出租人 / 承租人 / 業者")
    else:
        result["對象"] = match.group(1)

    # _檢查
    match = re.search(r"補助費用清冊_", path.name)
    if not match:
        return False, result, "補助費用清冊後用符號'_'接續"
        # errors.append("應為民國年份")
    else:
        result["符號"] = match.group(0)

    #民國年
    match = re.search(r"補助費用清冊_(1\d{2})", path.name)
    if not match:
        return False, result, "應為民國年份"
        # errors.append("應為民國年份")
    else:
        result["年份"] = match.group(1)
    # 月
    match = re.search(r"補助費用清冊_(1\d{2})(0[1-9]|1[0-2])", path.name)
    if not match:
        return False, result, "月份應為 01~12"
    else:
        result["月份"] = match.group(2)

    
    return True, result, "格式正確"
        
    
def is_valid_company(name_code = ""):
    
    mapping_df = pd.read_excel(MAPPING_FILE,
                        sheet_name="4-1",
                        header=0)
    # mapping_df[['縣市', '縣市代碼']] = mapping_df[['縣市', '縣市代碼']].ffill()
    mapping_df.loc[:, ['縣市', '縣市代碼', '業者名稱', '系統業者代號']] = mapping_df.loc[:, ['縣市', '縣市代碼', '業者名稱', '系統業者代號']].ffill()
    
    result = mapping_df[mapping_df['系統業者代號']==name_code]
    
    if not result.empty:
        result = result.iloc[0].to_dict()
        return True, result, f"與內容相同"
    else:
        return False, None, f"與內容相異"

def is_valid_suffix(file: Path):
    if file.suffix in [".xlsx", ".xls"]:
        return True, file.suffix, "副檔名正確"
    else:
        return False, file.suffix, "副檔名錯誤"

def is_readable_file(file):
    head = load_schema(file, header_rows=[1])
    schema = load_schema(file, header_rows=[2, 3])
    df = load_schema(file, header_rows=0)
    if df != None and schema != None and head != None:
        # print(head)
        # print(schema)
        # print(df)
        return True, [head, schema, df], "讀取成功"
    
    else:
        return False, None, f"讀取失敗: {head} / {df}"
    
def is_valid_period(period: str):
    # period check
    if period[:-1] in PERIOD:    
        return True, period[:-1], "  期別正確"
    else:
        return False, None, "期別錯誤"

def is_valid_year(year):
    # year check
    if is_int(year[:-1]):
        if MIN_YEAR <= int(year[:-1]) <= MAX_YEAR:
            # 
            return True, int(year[:-1]), "年限正確"
        else:
            return False, None, "年限錯誤"
    else:
        return False, None, "年限須為羅馬數字"
    
def is_valid_county(county):
    # county check
    if county in COUNTY:
        return True, county, "縣市正確"
    else :

        return False, None, "縣市錯誤"
    
def is_valid_month(month):
    # month check
    
    if is_int(month[:-1]):
        if 1 <= int(month[:-1]) <= 12:          
            return True, int(month[:-1]), "月份正確" 
        else:
            return False, None, "月份錯誤"
    else:
        return False, None, "月份須為羅馬數字"
        
