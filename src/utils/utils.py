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


class Result():
    def __init__(self,
                 file_name: str,
                 ):
        self.fname = file_name
        self.check_level = None
        self.result = self._create_default_result()
        
    def _create_default_result(self) -> dict:
        """回傳result模板

        Args:
            name (str): 模板名稱:
                'file_validator', 'schema_validator', 'logic_validator'

        Returns:
            dict: result模板
        """
        return {
            "file_validator": {
                "status": True,
                "message": "",
                "errors": {}
            },
            "schema_validator": {
                "status": True,
                "message": "",
                "errors": {}
            },
            "logic_validator": {
                "status": True,
                "message": "",
                "errors": {}
            },
            "info": {
            },
            "row_info": {}
        }

    def set_checklevel(self, check_level: str):
        """
        Args:
            check_level (str): 模板名稱:
                'file_validator', 'schema_validator', 'logic_validator'
        """
        self.check_level = check_level

    def update_status(self):
        
        if self.result[self.check_level]["errors"] != {}:
            self.result[self.check_level]["status"] = False
        # for k, v in self.result[self.check_level]["errors"].items():
        #     pass

    def get_status(self, check_level = None) -> bool:
        if check_level is None:
            return self.result[self.check_level]["status"]
        else:
            return self.result[check_level]["status"]

    def insert_error(self, item: str, msg: str):
        # if self.result[self.check_level]["errors"].get(item, True):
        #     self.result[self.check_level]["errors"][item] += msg
        # else:
            self.result[self.check_level]["errors"][item] = msg

    def get_error(self, check_level: str):
        # if self.result[self.check_level]["errors"].get(item, True):
        #     self.result[self.check_level]["errors"][item] += msg
        # else:
            return self.result[check_level]["errors"]
   
    def insert_info(self, item: str, info):
        self.result["info"][item] = info

    def get_info(self, item: str):
        return self.result["info"][item]

    # 目前只有在 logic_validator使用---
    def get_column(self):
        file_type = self.get_info("表種")
        if file_type == "表4":
            return ["媒合編號", "受款人", "費用"]
        elif file_type == "表7":
            return ["媒合編號", "受款人", "費用"]
        elif file_type == "表9":
            return ["媒合編號", "受款人", "案件", "費用", "起訖日"]
  
    def set_currentrow(self, index: int):
        self.index = str(index)

    def create_rowinfo(self):
        self.result["row_info"][self.index] = {}
    
    def insert_rowinfo(self, key, value):
        self.result["row_info"][self.index][key] = value

    def get_rowinfo(self, index: str|int):
        # 回傳rowdata中需要的傳遞資訊
        return self.result["row_info"][str(index)]
    
    def create_rowerror(self):
        column = self.get_column()
        self.result[self.check_level]["errors"][self.index] = dict.fromkeys(column, np.nan)

    def insert_rowerror(self, item: str, msg: str):
        self.result[self.check_level]["errors"][self.index][item] = msg

    # not yet
    def update_rowstatus(self, item: str):
        # row errors -> status and message
        # self.result[self.check_level]["errors"]
        pass
    # ---------------------------

    # 正規化csv 單個row的資訊
    def normalize_row(self, row):
        file_type = self.get_info("表種")
        if file_type == "表4":
            _, number, insurance_apply, insurance_cash, notarization_apply, notarization_cash, repair_apply, repair_cash, name, id, id_bank, id_branch, account = row[:13]
            self.cashlist = ["保險費", "公證費", "修繕費"]
            self.normdict = {
                "媒合編號": number,
                "保險費": insurance_cash,
                "公證費": notarization_cash,
                "修繕費": repair_cash,
                "姓名": name,
                "身分證": id, 
                "銀行代碼": id_bank, 
                "分行代碼": id_branch,
                "帳號": account
            }

        elif file_type == "表7":
            _, number, notarization_apply, notarization_cash, rental_cash, rental_period, rental_totalperiod, rental_type, name, id, id_bank, id_branch, account = row[:13]
            self.cashlist = ["公證費", "租金補助"]
            self.normdict = {
                "媒合編號": number,
                "公證費": notarization_cash,
                "租金補助": rental_cash,
                "租金期別": rental_period,
                "租金總期別": rental_totalperiod,
                "姓名": name,
                "身分證": id,
                "銀行代碼": id_bank, 
                "分行代碼": id_branch,
                "帳號": account
            }
        elif file_type == "表9":
            _, number, case_1, case_2, case_3, case_4, case_5, case_6, date_start, date_end, notarization_cash, development_cash, management_cash, management_period, management_totalperiod, matching_cash, custody_cash, custody_period, custody_totalperiod = row[:19]
            self.cashlist = ["公證費", "開發費", "包管費", "媒合費", "代管費" ]
            self.caselist = ["新件", "長者換居", "既存", "舊案", "換業者" ]
            self.normdict = {
                "媒合編號": number,
                "公證費": notarization_cash,
                "開發費": development_cash, 
                "包管費": management_cash,
                "包管費期別": management_period,
                "包管費總期別": management_totalperiod,
                "媒合費": matching_cash, 
                "代管費": custody_cash,
                "代管費期別": management_period,
                "代管費總期別": management_totalperiod,
                "新件": case_1,
                "長者換居": case_2,
                "既存": case_3,
                "舊案": case_4,
                "續約": case_5,
                "換業者": case_6,
                "租起日": date_start,
                "租訖日": date_end
            }
    
    def get_row(self, item: str):
        return self.normdict[item]
    
    def get_cashlist(self):
        return self.cashlist
    
    def get_caselist(self):
        return self.caselist
    # --------------------------- 

    def show(self):
        for k, v in self.result.items():
            if "validator" in k:
                print(k, v)

    
    def format_cell(self, df):

        for idx, row in df.iterrows():
            for col, val in row.items():

                if pd.isna(val):         # None 或 NaN
                    if col == "媒合編號":
                        item = self.get_rowinfo(idx)
                        df.at[idx, col] =  f"✔ {item['媒合編號']}"
                    else:
                        df.at[idx, col] = "✔"
                else:
                    df.at[idx, col] = f"✖ {val}"    # 有錯誤訊息
        return df
    
    def to_dataframe(self):

        
            
        df = pd.DataFrame.from_dict(self.result[self.check_level]["errors"], orient='index')
        df.index = df.index.astype(int)  # 若要整數 index
        
        df = df.sort_index()

        return self.format_cell(df)
    
def is_int(s):
    try:
        return int(s)
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