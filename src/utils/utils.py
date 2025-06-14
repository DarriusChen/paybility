import configparser
import pandas as pd
from pathlib import Path
import logging
from logger import format_func_msg

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

#  result template
def attribute(status=False, info=None, message=""):
    return {"status": status, "info": info, "message": message}

def get_dict_template(name: str):
    """回傳result模板

    Args:
        name (str): 模板名稱:
            'path_check', 'file_check', 'filename_check', 'schema_check'

    Returns:
        dict: result模板
    """
    template = {"status": attribute()}
    
    if name == "path_check":
        sub_status = {
            "period": attribute(),
            "county": attribute(),
            "year": attribute(),
            "month": attribute()
        }
        template["sub_status"] = sub_status
    elif name == "file_check":
        sub_status = {
            "suffix": attribute(),
            "exist": attribute(),
            "readable": attribute()
        }
        template["sub_status"] = sub_status
    elif name == "filename_check":
        sub_status = {
            "table":attribute(),
            "companycode": attribute()
            
        }
        template["sub_status"] = sub_status
    elif name == "schema_check":
        sub_status = {
            "entity_code": attribute(),
            "column_name": attribute()
        }
        template["sub_status"] = sub_status
    elif name == "logic_check":
        sub_status = {
            
            "error_row": attribute(info=[]), # 記錄所有error的list id
            "match_number": attribute(), # 記錄每個row媒合編號的情況 
            "recipient": attribute(), # 記錄每個row申請人/受款人的情況 Return bool, recipient_list([]), message
            "case_unique": attribute(), # 記錄每個row案件的唯一性(表九) Return bool, casetype_list, message
            "cash_unique": attribute(), # 記錄每個row金額的唯一性 Return bool, cashtype_list, message
            "cash": attribute(), # 記錄每個row金額的情況 (not yet) Return bool, value_list, message
        }
    elif name == "match_number_check":
        sub_status = {
            "id_company": attribute(),
            "id_countycode": attribute(),
            "type": attribute(),
            "numbertype": attribute(),
            "account": attribute(),
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
        print(type(df))
        return df
    except Exception as e:
        logger.error(format_func_msg(func='load_data', msg=f"讀取資料時發生錯誤: {e}"))
        return None
