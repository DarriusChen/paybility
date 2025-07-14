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

def validate_logic(dataframe: list,
                    file_type: str,
                    phase: str, 
                    county: str,
                    county_code: str) -> dict:
    
    logic_result = get_dict_template("logic_check")

    for i, row_content in enumerate(dataframe[2]):
        
        
        if file_type == "表4":
            row, number, insurance_apply, insurance_fee, notarization_apply, notarization_fee, repair_apply, repair_fee, name, id_name, id_bank, id_branch, account = row_content[:13]
            
            # 通表檢查 媒合編號邏輯
            match_number_result = valid_matching_number(str(number), phase,  county_code)
            if match_number_result["status"]["status"] == False:
                logic_result["sub_status"]["match_numbers"]["status"] = False
            logic_result["sub_status"]["match_numbers"]["info"].append(match_number_result)

            if match_number_result["status"]["status"]:

                # 受款人檢查
                recipient_result = valid_recipientinfo([name, id_name, str(int(id_bank)), str(int(id_branch)), str(int(account))])

                if recipient_result["status"]["status"] == False:
                    logic_result["sub_status"]["recipients"]["status"] = False
                logic_result["sub_status"]["recipients"]["info"].append(recipient_result)
                # 費用唯一性檢查
                unique_result = valid_uniqueinfo([insurance_fee, notarization_fee, repair_fee], ["保險費", "公證費", "修繕費"])

                if unique_result["status"]["status"] == False:
                    logic_result["sub_status"]["cash_uniques"]["status"] = False
                logic_result["sub_status"]["cash_uniques"]["info"].append(unique_result)


        elif file_type == "表7":
            
            row, number, notarization_apply, notarization_fee, rental_fee, rental_period, rental_totalperiod, rental_type, name, id_name, id_bank, id_branch, account = row_content[:13]
            

            match_number_result = valid_matching_number(str(number), phase,  county_code)
            if match_number_result["status"]["status"] == False:
                logic_result["sub_status"]["match_numbers"]["status"] = False
            logic_result["sub_status"]["match_numbers"]["info"].append(match_number_result)

            if match_number_result["status"]["status"]:
                # print(row_content)
                # 受款人檢查
                recipient_result = valid_recipientinfo([name, id_name, str(int(id_bank)), str(int(id_branch)), str(int(account))])

                if recipient_result["status"]["status"] == False:
                    logic_result["sub_status"]["recipients"]["status"] = False
                logic_result["sub_status"]["recipients"]["info"].append(recipient_result)
                # 費用唯一性檢查
                unique_result = valid_uniqueinfo([notarization_fee, rental_fee], ["公證費", "租金補助"])

                if unique_result["status"]["status"] == False:
                    logic_result["sub_status"]["cash_uniques"]["status"] = False
                logic_result["sub_status"]["cash_uniques"]["info"].append(unique_result)

        elif file_type in "表9":
            row, number, case_1, case_2, case_3, case_4, case_5, case_6, date_start, date_end, notarization_fee, development_fee, management_fee, management_period, management_totalperiod, matching_fee, custody_fee, custody_period, custody_totalperiod = row_content[:19]
            
            match_number_result = valid_matching_number(str(number), phase,  county_code)
            if match_number_result["status"]["status"] == False:
                logic_result["sub_status"]["match_numbers"]["status"] = False
            logic_result["sub_status"]["match_numbers"]["info"].append(match_number_result)

            if match_number_result["status"]["status"]:
             
                # 案件唯一性檢查
                caseunique_result = valid_uniqueinfo([case_1, case_2, case_3, case_4, case_5, case_6], ["新件", "長者換居", "既存", "舊案", "續約", "換業者"])
                if caseunique_result["status"]["status"] == False:
                    logic_result["sub_status"]["case_uniques"]["status"] = False
                logic_result["sub_status"]["case_uniques"]["info"].append(caseunique_result)

                # 費用唯一性檢查
                cashunique_result = valid_uniqueinfo([notarization_fee, development_fee, management_fee, matching_fee, custody_fee], ["公證費","開發費", "包管費", "媒合費", "代管費"])
                if cashunique_result["status"]["status"] == False:
                    logic_result["sub_status"]["cash_uniques"]["status"] = False
                logic_result["sub_status"]["cash_uniques"]["info"].append(cashunique_result)

                # 時間檢查
                date_result = valid_dateinfo([date_start, date_end])

                if date_result["status"]["status"] == False:
                    logic_result["sub_status"]["dates"]["status"] = False
                logic_result["sub_status"]["dates"]["info"].append(date_result)
        else:
            logic_result["status"]["status"] = False
            logic_result["status"]["info"] = file_type
            logic_result["status"]["message"] = "❌ 表單錯誤"


    if (logic_result["sub_status"]["match_numbers"]["status"] and
        logic_result["sub_status"]["recipients"]["status"] and
        logic_result["sub_status"]["cash_uniques"]["status"] and
        logic_result["sub_status"]["case_uniques"]["status"] and 
        logic_result["sub_status"]["dates"]["status"] and
        logic_result["sub_status"]["fees"]["status"]):

        logic_result["status"]["status"] = True
        logic_result["status"]["info"] = None
        logic_result["status"]["message"] = "表單內容正確"
    else:
        logic_result["status"]["status"] = False
        logic_result["status"]["info"] = None
        logic_result["status"]["message"] = "表單內容錯誤"

    return logic_result