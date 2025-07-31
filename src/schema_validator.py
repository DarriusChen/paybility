import pandas as pd
import configparser
from pathlib import Path
import logging
from logger import setup_logger, format_func_msg

from utils.utils import LOG_PATH, TEMPLETE_PATH, get_dict_template, load_data, load_schema, MAPPING_FILE


logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

# TODO: 業者代碼資料庫
# 2025/07/02: 此功能移至 filevalidator
# # entity_mapping_df = load_data(path=MAPPING_FILE,
#                         sheet_name="4-1",
#                         header_rows=[0],
#                         index_col=[0],
#                         logger=logger)

# 2025/07/02: move to file validator


# not use 2025/07/02
# def validate_entity_code(county: str, entity_code: str) -> bool:
#     """驗證業者代碼是否符合格式。
    
#     Args:
#         entity_code: 業者代碼
#     Returns:
#         bool: 是否符合格式
#     """
#     try:
#         entity_names = entity_mapping_df.loc[(county)]["系統業者代號"].tolist()
#         for name in entity_names:
#             if entity_code == name:
#                 return True
#             else:
#                 return False
#     except Exception as e:
#         logger.error(format_func_msg(func='validate_entity_code', msg=f"讀取業者代碼時發生錯誤: {e}"))
#         return None


def validate_schema(file_type: str,
                  data_file: list,
                  company_code: str,
                  logger: logging.Logger = logger) -> dict:
    """驗證資料是否符合模板，並回傳驗證結果。
    
    Args:
        file_type: 表種
        data_file: 資料檔案路徑
        logger: 日誌記錄器
    Returns:
        dict: 驗證結果
    """

    template_file = f"{TEMPLETE_PATH}/增辦第4期-表{file_type[-1]}.xlsx"

    schema_result = get_dict_template("schema_check")
    
    
    if file_type == "表9":
        template_columns = load_schema(path=template_file)[:20]
        data_columns = data_file[1][:20]
    elif file_type == "表4" or file_type == "表7":
        template_columns = load_schema(path=template_file)[:14]
        data_columns = data_file[1][:14]
    else:
        schema_result['status']['status'] = False
        schema_result['status']['info'] = None
        schema_result['status']['message'] = " 表單錯誤"
      
    if not isinstance(template_columns, list):
        logger.error(
            format_func_msg(func='validate_data', msg=f"讀取 schema 時發生錯誤: {template_columns}"))
        schema_result['status']['info'] = str(template_columns)
        schema_result['status']['message'] = " 讀取Template結構失敗"

        return schema_result

    logger.info(format_func_msg(func='validate_data', msg="開始驗證資料..."))

    error_messages = []
    

    # 驗證欄位數量是否符合模板
    template_columns_len = len(template_columns)
    data_columns_len = len(data_columns)
    if template_columns_len != data_columns_len:
        error_msg = (f"資料欄位數量與模板不符: "
                     f"template: {len(template_columns)}, "
                     f"data: {len(data_columns)}")
        logger.error(format_func_msg(func='validate_data', msg=error_msg))
        error_messages.append(error_msg)

        schema_result['sub_status']['表格名稱']['status'] = False
        schema_result['sub_status']['表格名稱']['info'] = f"{file_type}"
        schema_result['sub_status']['表格名稱']['message'] = "錯誤"
    else:
        schema_result['sub_status']['表格名稱']['status'] = True
        schema_result['sub_status']['表格名稱']['info'] = f"{file_type}"
        schema_result['sub_status']['表格名稱']['message'] = "正確"


    # 驗證欄位名稱是否符合模板
    error_columns = []
    compare_columns = {
        template_columns_len: template_columns,
        data_columns_len: data_columns
    }

    # 如果欄位數量不符，則補齊空欄位，使兩者欄位數量相同
    if template_columns_len != data_columns_len:
        difference_columns = max(template_columns_len, data_columns_len) - min(
            template_columns_len, data_columns_len)
        shorter_columns = compare_columns[min(template_columns_len,
                                              data_columns_len)]
        shorter_columns_len = len(shorter_columns)
        columns_padding = [""] * difference_columns
        shorter_columns.extend(columns_padding)
        compare_columns[shorter_columns_len] = shorter_columns

    for col_1, col_2 in zip(compare_columns[template_columns_len],
                            compare_columns[data_columns_len]):
        if col_1 != col_2:
            if col_2 not in ["序號" , "媒合編號"]:
                err_col = col_2.split["_"][-1]
            else:
                err_col = col_2.split["_"][0]
            error_columns.append(err_col)

    if error_columns:
        error_msg = f"資料中與模板中不一致的欄位: {error_columns}"
        logger.error(format_func_msg(func='validate_data', msg=error_msg))
        error_messages.append(error_msg)

        schema_result['sub_status']['表格名稱']['status'] = False
        schema_result['sub_status']['表格名稱']['info'] = len(error_columns)
        schema_result['sub_status']['表格名稱']['message'] = "錯誤"
        validation_passed = False
    else:
        schema_result['sub_status']['表格名稱']['status'] = True
        schema_result['sub_status']['表格名稱']['info'] = len(error_columns)
        schema_result['sub_status']['表格名稱']['message'] = "正確"
    
    entity_info = data_file[0]
    if "業者" in entity_info[0]:
        entity_code = entity_info[2]
        # print(entity_code, company_code)
        if entity_code == company_code:
            schema_result['sub_status']['業者代碼']['status'] = True
            schema_result['sub_status']['業者代碼']['info'] = entity_code
            schema_result['sub_status']['業者代碼']['message'] = "正確"
        else:
            schema_result['sub_status']['業者代碼']['status'] = False
            schema_result['sub_status']['業者代碼']['info'] = f"{company_code} {entity_code}"
            schema_result['sub_status']['業者代碼']['message'] = "錯誤，請確認業者代碼是否正確"


    else:
        schema_result['sub_status']['業者代碼']['status'] = False
        schema_result['sub_status']['業者代碼']['info'] = entity_info[0]
        schema_result['sub_status']['業者代碼']['message'] = f"錯誤: {entity_info[0]} - {entity_info[2]}"

    

    # 返回結果結構
    if (schema_result['sub_status']['業者代碼']['status'] and 
        schema_result['sub_status']['表格名稱']['status']):
        schema_result['status']['status'] = True
        schema_result['status']['info'] = None
        schema_result['status']['message'] = "欄位結構正確"

        logger.info(
        format_func_msg(func='validate_data',
                        msg=f"驗證完成，結果: {'通過'}"))
    else:
        schema_result['status']['status'] = False
        schema_result['status']['info'] = f"錯誤訊息: {'; '.join(error_messages)}"
        schema_result['status']['message'] = " 欄位結構錯誤"

        logger.info(
        format_func_msg(func='validate_data',
                        msg=f"驗證完成，結果: {'失敗'}"))

    return schema_result