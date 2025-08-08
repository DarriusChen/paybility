
import pandas as pd
import re

from pathlib import Path
from logger import setup_logger, format_func_msg
from utils.utils import LOG_PATH, MAPPING_FILE, load_schema, Result

logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')
     
def validate_path(file, result: Result):
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

    result.set_checklevel("file_validator")

    if check_name(path, result):
    
        is_readable_file(file, result)

        is_valid_company(result)
    

    result.update_status()
        
    
def check_name(path, result: Result):

    # 表4_、表7_、表9_
    match = re.match(r"^(表4|表7|表9)_", path.name)
    if not match:
        result.insert_error("檔案名稱", "應為表4、表7、表9，並以符號'_'接續")
        return False
    else:
        result.insert_info("表種", match.group(1))

    # 2~4個中文字
    match = re.search(r"^(表4|表7|表9)_([\u4e00-\u9fff]{2,4})", path.name)

    if not match:
        result.insert_error("檔案名稱", "應為2到4個中文字的業者代碼")
        return False
    else:
        result.insert_info("業者代碼", match.group(2))

    # 期別
    match = re.search(r"([\u4e00-\u9fff]{2,4})(1|2|3|31|4|41)期", path.name)

    if not match:
        result.insert_error("檔案名稱", "期數應為 1、2、3、31、4或41，並以'期'結尾")
        return False
    else:
        result.insert_info("期別", match.group(2))


    # 對象
    match = re.search(r"(出租人|承租人|業者服務)補助費用清冊", path.name)

    if not match:
        result.insert_error("檔案名稱", "對象應為: 出租人、承租人、業者")
        return False
    else:
        result.insert_info("對象", match.group(1))

    # _檢查

    match = re.search(r"補助費用清冊_", path.name)

    if not match:
        result.insert_error("檔案名稱", "補助費用清冊後用符號'_'接續")
        return False
    else:
        # result["info"]["符號"] = match.group(0)
        pass

    #民國年
    match = re.search(r"補助費用清冊_(1\d{2})", path.name)

    if not match:
        result.insert_error("檔案名稱", "應為民國年份")
        return False
    else:
        result.insert_info("年份", match.group(1))

    # 月
    match = re.search(r"補助費用清冊_(1\d{2})(0[1-9]|1[0-2])", path.name)

    if not match:
        result.insert_error("檔案名稱", "月份應為 01~12")
        return False
    else:
        result.insert_info("月份", match.group(2))

    return True
        
def is_readable_file(file, result: Result):
    
    head = load_schema(file, header_rows=[1])
    if not isinstance(head, list):
        result.insert_error("讀取狀態", head)
    else:
        result.insert_info("表單業者代碼", head[2])

    schema = load_schema(file, header_rows=[2, 3])
    if not isinstance(schema, list):
        result.insert_error("讀取狀態", schema)
    else:
        result.insert_info("表格格式", schema)
    
    df = load_schema(file, header_rows=0)
    if not isinstance(df, list):
        result.insert_error("讀取狀態", df)
    else:
        result.insert_info("表格內容", df[1:]) # update_dataframe

def is_valid_company(result: Result):
    company_code = result.get_info("業者代碼")
    company_code_indataframe = result.get_info("表單業者代碼")
    # Todo: 改成SQL

    mapping_df = pd.read_excel(MAPPING_FILE,
                        sheet_name="4-1",
                        header=0)
    # mapping_df[['縣市', '縣市代碼']] = mapping_df[['縣市', '縣市代碼']].ffill()
    mapping_df.loc[:, ['縣市', '縣市代碼', '業者名稱', '系統業者代號']] = mapping_df.loc[:, ['縣市', '縣市代碼', '業者名稱', '系統業者代號']].ffill()
    
    filtered = mapping_df[mapping_df['系統業者代號'] == company_code]
    # print(filtered)
    # print(company_code, company_code_indataframe, mapping_dict.get("系統業者代號"))
    if not filtered.empty:
        mapping_dict = filtered.iloc[0].to_dict()

        if mapping_dict.get("縣市"):
            result.insert_info("縣市", mapping_dict.get("縣市"))
        else:
            result.insert_error("業者資訊", "無縣市資訊")
        
        if mapping_dict.get("縣市代碼"):
            result.insert_info("縣市代碼", mapping_dict.get("縣市代碼"))
        else:
            result.insert_error("業者資訊", "無縣市代碼")

        if mapping_dict.get("業者名稱"):
            result.insert_info("業者名稱", mapping_dict.get("業者名稱"))
        else:
            result.insert_error("業者資訊", "無業者名稱")

        if mapping_dict.get("系統業者代號"):

            if company_code != company_code_indataframe:
                result.insert_error("業者資訊", f"檔案名稱({company_code})與表單內容({company_code_indataframe})業者代號不同")
            else:

                result.insert_info("業者代碼", mapping_dict.get("系統業者代號"))
        else:
            result.insert_error("業者資訊", "無業者代號")

    else:
        result.insert_error("業者資訊", f"無匹配資料請確認資料庫中正確的業者代號")

    

        
