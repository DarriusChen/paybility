import configparser
import json
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from logger import format_func_msg
from typing import Any, List

config = configparser.ConfigParser()
config.read('config.ini')

# Path Parameter
MAX_YEAR = int(config['path_parameter']['max_year'])
MIN_YEAR = int(config['path_parameter']['min_year'])
PERIOD = config.get('path_parameter', 'period').split(',')
COUNTY = config.get('path_parameter', 'county').split(',')
TABLES = config.get('path_parameter', 'tables').split(',')
# Path Config
RESULT_PATH = config['output_path']['result_path']
LOG_PATH = config['output_path']['log_path']
TEMPLETE_PATH = config['output_path']['template_path']
MAPPING_FILE = config['output_path']['mapping_file']

# print(MAX_YEAR, MIN_TEAR, PERIOD, COUNTY, TABLES)

# norm_row_content
def norm_rowcontent(file_type: str, row: list):
    if file_type == "表4":
        _, number, insurance_apply, insurance_cash, notarization_apply, notarization_cash, repair_apply, repair_cash, name, id, id_bank, id_branch, account = row[:13]

        cash_dict =  {
            "保險費": insurance_cash,
            "公證費": notarization_cash,
            "修繕費": repair_cash
        }
        recipient_dict = { 
            "姓名": name,
            "身分證": id, 
            "銀行代碼": str(int(id_bank)), 
            "分行代碼": str(int(id_branch)),
            "帳號": str(int(account))
        }

        return str(number), recipient_dict, cash_dict
        
    elif file_type == "表7":
        _, number, notarization_apply, notarization_cash, rental_cash, rental_period, rental_totalperiod, rental_type, name, id, id_bank, id_branch, account = row[:13]

        cash_dict =  {
            "公證費": notarization_cash,
            "租金補助": [rental_cash, rental_period, rental_totalperiod]
        }

        recipient_dict = { 
            "姓名": name,
            "身分證": id, 
            "銀行代碼": str(int(id_bank)), 
            "分行代碼": str(int(id_branch)),
            "帳號": str(int(account))
        }

        return str(number), recipient_dict, cash_dict
        
    elif file_type == "表9":
        _, number, case_1, case_2, case_3, case_4, case_5, case_6, date_start, date_end, notarization_cash, development_cash, management_cash, management_period, management_totalperiod, matching_cash, custody_cash, custody_period, custody_totalperiod = row[:19]
    
        cash_dict =  {
            "公證費": notarization_cash,
            "開發費": development_cash, 
            "包管費": [management_cash, management_period, management_totalperiod], 
            "媒合費": matching_cash, 
            "代管費": [custody_cash, custody_period, custody_totalperiod]
        }

        case_dict = {   
            "新件": case_1,
            "長者換居": case_2,
            "既存": case_3,
            "舊案": case_4,
            "續約": case_5,
            "換業者": case_6
        }

        date_dict = {
            "租起日": date_start,
            "租訖日": date_end
        }

        return str(number), case_dict, cash_dict, date_dict

    else:
        raise Exception(f"表種錯誤: {file_type}")

#  result template
def attribute(status=False, info=None, message="未檢查"):
    return {"status": status, "info": info, "message": message}

def get_dict_template(name: str):
    """回傳result模板

    Args:
        name (str): 模板名稱:
            'path_check', 'file_check', 'schema_check'

    Returns:
        dict: result模板
    """
    template = {"status": attribute()}
    
    if name == "file_check":
        sub_status = {
            "檔案名稱": attribute(),
            # "suffix": attribute(),
            # "exist": attribute(),
            "讀取": attribute(),
            "業者代碼": attribute()
        }
        template["sub_status"] = sub_status
    elif name == "schema_check":
        sub_status = {
            "業者代碼": attribute(),
            "表格名稱": attribute()
        }
        template["sub_status"] = sub_status
    elif name == "logic_check":
        sub_status = {
            "match_numbers": attribute(status=True, info=[]), # 記錄每個row媒合編號的情況 
            "recipients": attribute(status=True, info=[]), # 記錄每個row申請人/受款人的情況 
            "cash_uniques": attribute(status=True, info=[]), # 記錄每個row金額的唯一性 
            "cashs": attribute(status=True, info=[]), # 記錄每個row金額的情況 (not yet) 
            "case_uniques": attribute(status=True, info=[]), # 記錄每個row案件的唯一性(表九)
            "dates": attribute(status=True, info=[]), # 記錄每個row時間的情況(表九)
            
        }
        template["sub_status"] = sub_status
    elif name == "matchnumber_check":
        sub_status = {
            "match_number": attribute(),
            "county": attribute(),
            "version": attribute(),
            "numbertype": attribute(),
            "contract": attribute(),
            "periodtype": attribute(),
            "serial_number": attribute()
        }

        template["sub_status"] = sub_status
    elif name == "recipient_check":
        sub_status = {
            "name": attribute(),
            "id_name": attribute(),
            "id_bank": attribute(),
            "id_branch": attribute(),
            "account": attribute(),
        }

        template["sub_status"] = sub_status
    elif name == "unique_check":
        sub_status = {
            "unique": attribute(),
        }

        template["sub_status"] = sub_status
    elif name == "date_check":
        sub_status = {
            "start": attribute(),
            "end": attribute(),
        }

        template["sub_status"] = sub_status
    elif name == "cash_check":
        sub_status = {
            "cash": attribute(),
            "period": attribute(),
            "apply": attribute(),
        }

        template["sub_status"] = sub_status
    else:
        return None
    return template

    
def is_int(s):
    try:
        int(s)
        return True
    except ValueError as e:
        return False

def is_nan(n):
    
    if pd.isna(n):
        return str(n)
    else:
        return n

def load_data(path: str | Path,
              header_rows: list[int],
              sheet_name: str = 0,
              index_col: list[int] = None,
              logger: logging.Logger = None) -> pd.DataFrame:
    """讀取資料。
    
    Args:
        path: 檔案路徑
    Returns:
        pd.DataFrame: 資料
    """
    try:
        df = pd.read_excel(path, sheet_name=sheet_name, header=header_rows, index_col=index_col)
        logger.info(format_func_msg(func='load_data',
                            msg=f"資料讀取成功: {path}"))

        return df
    except Exception as e:
        logger.error(format_func_msg(func='load_data', msg=f"讀取資料時發生錯誤: {e}"))

        return None
    
def load_schema(path,
                header_rows: list[int] = [2, 3],
                sheet: int = 0 ) -> list[str]:
    """讀取雙層表頭並攤平成單層欄位。
    
    Args:
        path: 檔案路徑
        header_rows: 表頭行數
        sheet: 工作表索引
        
    Returns:
        pd.DataFrame: 攤平後的 DataFrame
    """
    try:
        df = pd.read_excel(path, sheet_name=sheet, header=header_rows)
        # → flatten MultiIndex columns and remove \n
        if header_rows == [1]:
            df.columns = [
                ''.join(str(c).strip().replace('\n', '') for c in col if str(c) != 'nan')
                for col in df.columns.values
            ]
            return df.columns.tolist()
        elif header_rows == [2, 3]:

            df.columns = [
                '_'.join(str(c).strip().replace('\n', '') for c in col if str(c) != 'nan')
                for col in df.columns.values
            ]
            return df.columns.tolist()
        else:
            arr = np.where(pd.isna(df), '', df)
            return arr[arr[:, 1] != ''].tolist()

        
    except Exception as e:

        return e

    

def print_pretty(data: Any, keys: List[str] = ["info", "error_row", "match_number", "recipient", "case_unique", "cash_unique", "date", "cash"]):
    # 標記指定欄位為 __ONELINE__
    def mark_oneline(obj):
        if isinstance(obj, dict):
            return {
                k: (
                    "__ONELINE__" + json.dumps(v, ensure_ascii=False)
                    if k in keys and isinstance(v, list)
                    else mark_oneline(v)
                )
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [mark_oneline(item) for item in obj]
        return obj

    # 將 __ONELINE__ 還原成原始 list 文字格式
    def restore_oneline(json_str):
        return json_str.replace('"__ONELINE__', '').replace(']"', ']')

    # 處理流程
    marked = mark_oneline(data)
    dumped = json.dumps(marked, ensure_ascii=False, indent=4)
    result = restore_oneline(dumped)
    print(result)