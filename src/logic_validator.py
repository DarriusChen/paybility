from pathlib import Path
import logging
from logger import setup_logger, format_func_msg
from utils.utils import LOG_PATH, MAPPING_FILE, get_dict_template, norm_rowcontent

from logic.unique_logic import valid_uniqueinfo
from logic.recipient_logic import valid_recipientinfo
from logic.cash_logic import valid_cash
from logic.matchnumber_logic import valid_matching_number
from logic.date_logic import valid_dateinfo
import os
from database import DatabaseService

logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

def validate_logic(dataframe: list,
                    file_type: str,
                    phase: str, 
                    county_code: str) -> dict:
    
    logic_result = get_dict_template("logic_check")

    for i, row_content in enumerate(dataframe[2]):
        # 依序檢查每個row的: 
        #   媒合編號 >> 受款人 >> (案件、金額)唯一性
        #   若(媒合編號、唯一性)錯誤: 則不進行金額檢查
        if i > 0:
            if file_type == "表4":
                number, recipient, cash = norm_rowcontent(file_type, row_content)
                # print(row_content[:13])
                # 通表檢查 媒合編號邏輯
                # print(number)
                match_number_result = valid_matching_number(number, phase, county_code)
                if match_number_result["status"]["status"] == False:
                    logic_result["sub_status"]["match_numbers"]["status"] = False
                logic_result["sub_status"]["match_numbers"]["info"].append(match_number_result)

                # 受款人檢查
                recipient_result = valid_recipientinfo(recipient)

                if recipient_result["status"]["status"] == False:
                    logic_result["sub_status"]["recipients"]["status"] = False
                logic_result["sub_status"]["recipients"]["info"].append(recipient_result)

                # 費用唯一性檢查
                unique_result = valid_uniqueinfo(cash)

                if unique_result["status"]["status"] == False:
                    logic_result["sub_status"]["cash_uniques"]["status"] = False
                logic_result["sub_status"]["cash_uniques"]["info"].append(unique_result)
                
                
                if match_number_result["status"]["status"] and unique_result["status"]["status"]:
                    # print(unique_result["status"]["info"], cash[unique_result["status"]["info"]])
                    cash_result = valid_cash(number=match_number_result["status"]["info"], 
                                        cash_type=unique_result["status"]["info"],
                                        cash=cash[unique_result["status"]["info"]],
                                        file_type=file_type)
                    

                #     # 檢查金額
                #     logic_result["sub_status"]["cash_uniques"]["info"].append(unique_result)


                # else:
                #     # (媒合編號、唯一性)錯誤: 不檢查
                    


            elif file_type == "表7":
                
                number, recipient, cash = norm_rowcontent(file_type, row_content)
                

                match_number_result = valid_matching_number(number, phase, county_code)
                if match_number_result["status"]["status"] == False:
                    logic_result["sub_status"]["match_numbers"]["status"] = False
                logic_result["sub_status"]["match_numbers"]["info"].append(match_number_result)

                # 受款人檢查
                recipient_result = valid_recipientinfo(recipient)

                if recipient_result["status"]["status"] == False:
                    logic_result["sub_status"]["recipients"]["status"] = False
                logic_result["sub_status"]["recipients"]["info"].append(recipient_result)

                # 費用唯一性檢查
                unique_result = valid_uniqueinfo(cash)

                if unique_result["status"]["status"] == False:
                    logic_result["sub_status"]["cash_uniques"]["status"] = False
                logic_result["sub_status"]["cash_uniques"]["info"].append(unique_result)

            elif file_type in "表9":
                number, case, cash, date = norm_rowcontent(file_type, row_content)

                match_number_result = valid_matching_number(number, phase,  county_code)
                if match_number_result["status"]["status"] == False:
                    logic_result["sub_status"]["match_numbers"]["status"] = False
                logic_result["sub_status"]["match_numbers"]["info"].append(match_number_result)

                # if match_number_result["status"]["status"]:
                
                # 案件唯一性檢查
                caseunique_result = valid_uniqueinfo(case)
                if caseunique_result["status"]["status"] == False:
                    logic_result["sub_status"]["case_uniques"]["status"] = False
                logic_result["sub_status"]["case_uniques"]["info"].append(caseunique_result)

                # 費用唯一性檢查
                cashunique_result = valid_uniqueinfo(cash)
                
                if cashunique_result["status"]["status"] == False:
                    logic_result["sub_status"]["cash_uniques"]["status"] = False
                logic_result["sub_status"]["cash_uniques"]["info"].append(cashunique_result)

                # 時間檢查
                date_result = valid_dateinfo(date)

                if date_result["status"]["status"] == False:
                    logic_result["sub_status"]["dates"]["status"] = False
                logic_result["sub_status"]["dates"]["info"].append(date_result)
            
            else:
                logic_result["status"]["status"] = False
                logic_result["status"]["info"] = file_type
                logic_result["status"]["message"] = "表單錯誤"


    if (logic_result["sub_status"]["match_numbers"]["status"] and
        logic_result["sub_status"]["recipients"]["status"] and
        logic_result["sub_status"]["cash_uniques"]["status"] and
        logic_result["sub_status"]["case_uniques"]["status"] and 
        logic_result["sub_status"]["dates"]["status"] and
        logic_result["sub_status"]["cashs"]["status"]):

        logic_result["status"]["status"] = True
        logic_result["status"]["info"] = None
        logic_result["status"]["message"] = "表單內容正確"
    else:
        logic_result["status"]["status"] = False
        logic_result["status"]["info"] = None
        logic_result["status"]["message"] = "表單內容錯誤"

    return logic_result