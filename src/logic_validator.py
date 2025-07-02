from pathlib import Path
import logging
from logger import setup_logger, format_func_msg
from utils.utils import LOG_PATH, MAPPING_FILE, get_dict_template, load_data, is_nan

from logic.unique_logic import valid_uniqueinfo
from logic.recipient_logic import valid_recipientinfo
# from logic.period_logic import valid_periodinfo
from logic.matchnumber_logic import valid_matching_number
from logic.date_logic import valid_dateinfo
import os

logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

def validate_logic(data_file: str | Path,
                    logger: logging.Logger,
                    tabletype: str,
                    phase: str) -> dict:
    
    logic_result = get_dict_template("logic_check")
    
    df = load_data(path=data_file,
                    header_rows=[2, 3],
                    logger=logger)

    error_list = []
    match_number_list = []
    recipient_list = []
    cash_unique_list = []
    case_unique_list = []
    cash_list = []
    date_list = []

    for index, row_content in df.iterrows():
        if tabletype in ["表4", "表單4", "表四", "表單四"]:
            row, number, insurance_apply, insurance_fee, notarization_apply, notarization_fee, repair_apply, repair_fee, name, id_name, id_bank, id_branch, account = row_content[:13]
            
            # 通表檢查 媒合編號邏輯
            match_number_result = valid_matching_number(str(number), phase)
            if match_number_result["status"]["status"]:

                # 受款人檢查
                recipient_result = valid_recipientinfo([name, id_name, str(int(id_bank)), str(int(id_branch)), str(int(account))])
                # 費用唯一性檢查
                unique_result = valid_uniqueinfo([insurance_fee, notarization_fee, repair_fee], "保險費", "公證費", "修繕費")
                # 期別檢查
                # period_result = valid_periodinfo() # not yet

                # print(match_number_result, recipient_result, unique_result)

                # os.system("pause")

                match_number_list.append(match_number_result)
                recipient_list.append(recipient_result)
                cash_unique_list.append(unique_result)
                case_unique_list.append(None)
                cash_list.append(None)
                date_list.append(None)

                if not (match_number_result["status"]["status"] and 
                    recipient_result["status"]["status"] and
                    unique_result["status"]["status"]):
                    error_list.append(row)

        elif tabletype in ["表7", "表單7", "表七", "表單七"]:
            row, number, notarization_apply, notarization_fee, rental_fee, rental_period, rental_totalperiod, rental_type, name, id_name, id_bank, id_branch, account = row_content[:13]
            
            # 通表檢查 媒合編號邏輯
            match_number_result = valid_matching_number(str(number), phase)
            if match_number_result["status"]["status"]:

                # 受款人檢查
                recipient_result = valid_recipientinfo([name, id_name, str(int(id_bank)), str(int(id_branch)), str(int(account))])
                # 費用唯一性檢查
                unique_result = valid_uniqueinfo([notarization_fee, rental_fee], ["公證費", "租金補助"])

                match_number_list.append(match_number_result)
                recipient_list.append(recipient_result)
                cash_unique_list.append(unique_result)
                case_unique_list.append(None)
                cash_list.append(None)
                date_list.append(None)

                if not (match_number_result["status"]["status"] and 
                    recipient_result["status"]["status"] and
                    unique_result["status"]["status"]):
                    error_list.append(row)

        elif tabletype in ["表9", "表單9", "表九", "表單九"]:
            row, number, case_1, case_2, case_3, case_4, case_5, case_6, date_start, date_end, notarization_fee, development_fee, management_fee, management_period, management_totalperiod, matching_fee, custody_fee, custody_period, custody_totalperiod = row_content[:19]
            
            # 通表檢查 媒合編號邏輯
            match_number_result = valid_matching_number(str(number), phase)
            if match_number_result["status"]["status"]:
             
                # 案件唯一性檢查
                caseunique_result = valid_uniqueinfo([case_1, case_2, case_3, case_4, case_5, case_6], ["新件", "長者換居", "既存", "舊案", "續約", "換業者"])
                # 費用唯一性檢查
                cashunique_result = valid_uniqueinfo([notarization_fee, development_fee, management_fee, matching_fee, custody_fee], ["公證費","開發費", "包管費", "媒合費", "代管費"])
                # 時間檢查
                date_result = valid_dateinfo([date_start, date_end])

                match_number_list.append(match_number_result)
              
                cash_unique_list.append(cashunique_result)
                case_unique_list.append(caseunique_result)
                cash_list.append(None)
                date_list.append(date_result)

                if not (match_number_result["status"]["status"] and 
                    cashunique_result["status"]["status"] and
                    caseunique_result["status"]["status"] and
                    date_result["status"]["status"]):
                    error_list.append(row)
        else:
            logic_result["status"]["status"] = False
            logic_result["status"]["info"] = tabletype
            logic_result["status"]["message"] = "❌ 表單錯誤"

    logic_result["sub_status"]["error_row"] = error_list
    logic_result["sub_status"]["match_number"] = match_number_list
    logic_result["sub_status"]["recipient"] = recipient_list
    logic_result["sub_status"]["cash_unique"] = cash_unique_list
    logic_result["sub_status"]["case_unique"] = case_unique_list
    logic_result["sub_status"]["date"] = date_list
    logic_result["sub_status"]["cash"] = cash_list

    if error_list == []:
        logic_result["status"]["status"] = True
        logic_result["status"]["info"] = None
        logic_result["status"]["message"] = "✅ 表單內容正確"
    else:
        logic_result["status"]["status"] = False
        logic_result["status"]["info"] = None
        logic_result["status"]["message"] = "❌ 表單內容錯誤"

    return logic_result
