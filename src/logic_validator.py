from pathlib import Path
import logging
from logger import setup_logger, format_func_msg
from utils.utils import LOG_PATH, Result

from logic.unique_logic import valid_uniquecase, valid_uniquecash
from logic.recipient_logic import valid_recipientinfo
from logic.cash_logic import valid_cash
from logic.matchnumber_logic import valid_matching_number
from logic.date_logic import valid_dateinfo
import os
from database import DatabaseService

logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

def validate_logic(result: Result):

    result.set_checklevel("logic_validator")

    dataframe = result.get_info("表格內容")
    file_type = result.get_info("表種")

    
    for i, row_content in enumerate(dataframe):
        # 依序檢查每個row的: 

        result.set_currentrow(i)
        result.create_rowinfo()
        result.create_rowerror()

        result.normalize_row(row_content)
        #   媒合編號 >> 受款人 >> (案件、金額)唯一性
        #   若(媒合編號、唯一性)錯誤: 則不進行金額檢查

        if file_type == "表4":
            # 媒合編號邏輯
            valid_matching_number(result)
            
            # 受款人檢查
            valid_recipientinfo(result)

            # 費用唯一性檢查
            valid_uniquecash(result)

            result.update_status()

            if result.get_status():
                # 費用唯一才進行費用檢查
                valid_cash(result)

        elif file_type == "表7":
            # 媒合編號邏輯
            valid_matching_number(result)
            
            # 受款人檢查
            valid_recipientinfo(result)

            # 費用唯一性檢查
            valid_uniquecash(result)

            result.update_status()

            if result.get_status():
                # 費用唯一才進行費用檢查
                valid_cash(result)
            # Todo
        elif file_type == "表9":
            # 媒合編號邏輯
            valid_matching_number(result)

            # 案件唯一性檢查
            valid_uniquecase(result)

            # 費用唯一性檢查
            valid_uniquecash(result)
            
            result.update_status()

            if result.get_status():
                # 案件、費用唯一才進行之後的 時間、費用檢查

                valid_dateinfo(result)
                valid_cash(result)

        result.update_status()