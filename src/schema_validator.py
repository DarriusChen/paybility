import pandas as pd
import configparser
from pathlib import Path
import logging
from logger import setup_logger, format_func_msg

from utils.utils import LOG_PATH, TEMPLETE_PATH, get_dict_template, load_data, MAPPING_FILE


logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

# TODO: 業者代碼資料庫
entity_mapping_df = load_data(path=MAPPING_FILE,
                        sheet_name="4-1",
                        header_rows=[0],
                        index_col=[0],
                        logger=logger)

def load_complex_schema(path: str | Path,
                        header_rows: list[int] = [2, 3],
                        sheet: int = 0) -> list[str]:
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
        df.columns = [
            '_'.join(str(c).strip().replace('\n', '') for c in col if str(c) != 'nan')
            for col in df.columns.values
        ]
        
    except Exception as e:
        logger.error(format_func_msg(func='load_complex_schema',
                                     msg=f"讀取檔案時發生錯誤: {e}"))
        return None

    logger.info(format_func_msg(func='load_complex_schema',
                                msg=f"檔案讀取成功: {path}"))

    return df.columns.tolist()

def validate_entity_code(county: str, entity_code: str) -> bool:
    """驗證業者代碼是否符合格式。
    
    Args:
        entity_code: 業者代碼
    Returns:
        bool: 是否符合格式
    """
    try:
        entity_names = entity_mapping_df.loc[(county)]["系統業者代號"].tolist()
        if entity_code in entity_names:
            return True
        else:
            return False
    except Exception as e:
        logger.error(format_func_msg(func='validate_entity_code', msg=f"讀取業者代碼時發生錯誤: {e}"))
        return None


def validate_schema(file_type: str,
                  data_file: str | Path,
                  county: str,
                  logger: logging.Logger = logger) -> dict:
    """驗證資料是否符合模板，並回傳驗證結果。
    
    Args:
        file_type: 表種
        data_file: 資料檔案路徑
        county: 縣市
        logger: 日誌記錄器
    Returns:
        dict: 驗證結果
    """

    template_file = f"{TEMPLETE_PATH}/增辦第4期-表{file_type[-1]}.xlsx"

    schema_result = get_dict_template("schema_check")
    

    try:
        if file_type in ["表9", "表單9"]:
            template_columns = load_complex_schema(path=template_file)[:20]
            data_columns = load_complex_schema(path=data_file)[:20]
        elif file_type in ["表4", "表單4", "表7", "表單7"]:
            template_columns = load_complex_schema(path=template_file)[:14]
            data_columns = load_complex_schema(path=data_file)[:14]

    except Exception as e:
        logger.error(
            format_func_msg(func='validate_data', msg=f"讀取 schema 時發生錯誤: {e}"))
        schema_result['status']['info'] = str(e)
        schema_result['status']['message'] = "❌ 讀取欄位結構失敗"
        schema_result['sub_status']['entity_code']['message'] = "❌ 無法驗證業者代碼"
        schema_result['sub_status']['column_name']['message'] = "❌ 無法驗證欄位名稱"

        return schema_result

    logger.info(format_func_msg(func='validate_data', msg="開始驗證資料..."))

    validation_passed = True
    error_messages = []
    schema_result['sub_status']['column_name']['status'] = True
    schema_result['sub_status']['column_name']['info'] = f"{file_type}"
    schema_result['sub_status']['column_name']['message'] = "✅ 欄位名稱及順序正確"

    # 驗證欄位數量是否符合模板
    template_columns_len = len(template_columns)
    data_columns_len = len(data_columns)
    if template_columns_len != data_columns_len:
        error_msg = (f"資料欄位數量與模板不符: "
                     f"template: {len(template_columns)}, "
                     f"data: {len(data_columns)}")
        logger.error(format_func_msg(func='validate_data', msg=error_msg))
        error_messages.append(error_msg)
        validation_passed = False

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
        schema_result['sub_status']['column_name']['info'] = len(error_columns)
        schema_result['sub_status']['column_name']['message'] = "❌ 欄位名稱錯誤"
        validation_passed = False

    # 驗證業者代碼是否符合格式
    schema_result['sub_status']['entity_code']['status'] = False
    df_entity_result = load_data(path=data_file,
                                 header_rows=[1],
                                 logger=logger
                                 )
    entity_info = df_entity_result.columns.tolist()
    if "業者" in entity_info[0]:
        entity_code = entity_info[2]
        if not validate_entity_code(county=county, entity_code=entity_code):
            schema_result['sub_status']['entity_code']['info'] = f"錯誤業者代碼: {entity_code}"
            schema_result['sub_status']['entity_code']['message'] = "❌ 業者代碼錯誤，請確認業者代碼是否正確"
            validation_passed = False
        else:
            schema_result['sub_status']['entity_code']['status'] = True
            schema_result['sub_status']['entity_code']['info'] = entity_code
            schema_result['sub_status']['entity_code']['message'] = "✅ 業者代碼正確"
    else:
        schema_result['sub_status']['entity_code']['info'] = entity_info[0]
        schema_result['sub_status']['entity_code']['message'] = f"❌ 業者代碼欄位名稱錯誤: {entity_info[0]} - {entity_info[2]}"
        validation_passed = False

    logger.info(
        format_func_msg(func='validate_data',
                        msg=f"驗證完成，結果: {'通過' if validation_passed else '失敗'}"))

    # 返回結果結構
    if validation_passed:
        schema_result['status']['status'] = True
        schema_result['status']['message'] = "✅ 欄位結構正確"
    else:
        schema_result['status']['info'] = f"錯誤訊息: {'; '.join(error_messages)}"
        schema_result['status']['message'] = "❌ 欄位結構錯誤"

    return schema_result