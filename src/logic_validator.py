from pathlib import Path
import logging
from logger import setup_logger, format_func_msg
from utils.utils import LOG_PATH, MAPPING_FILE, get_dict_template, load_data, is_nan

from logic.unique_logic import valid_uniqueinfo
from logic.recipient_logic import valid_recipientinfo
from logic.period_logic import valid_periodinfo
from logic.matchnumber_logic import valid_matching_number



logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

def validate_logic(data_file: str | Path,
                    logger: logging.Logger,
                    tabletype: str,
                    phase: str) -> dict:
    
    logic_result = get_dict_template("logic_check")

    # try:
    df = load_data(path=data_file,
                    header_rows=[2, 3],
                    logger=logger)

    error_list = []
    match_number_list = []
    recipient_list = []
    case_unique_list = []
    cash_unique_list = []
    cash_list = []

    for index, row_content in df.iterrows():
        if tabletype == "表四":
            row, number, _, _, _, _, _, _, name, id_name, id_bank, id_branch, account = row_content[:13]
            if isinstance(number, str):
                # print(row, type(number), _, _, _, _, _, _, name, id_name, id_bank, id_branch, account)
                match_number_result = valid_matching_number(number, phase)
                recipient_result = valid_recipientinfo([name, id_name, id_bank, id_branch, account], get_dict_template("recipient_check"))
                # period_result = valid_periodinfo
                print(match_number_result)
        elif tabletype == "表七":
            pass
        elif tabletype == "表九":
            pass
        else:
            "error"



    # except Exception as e:
    #     print(e)

validate_logic(r"C:\xiaofu\工作\2025\國家住宅及都市管理中心\付款清冊清理\paybility\data\41期\114年\台中\3月\[enc]表4_匯揚41期出租人補助費用清冊_11403.xlsx"
              , logger , "表四", "匯揚")