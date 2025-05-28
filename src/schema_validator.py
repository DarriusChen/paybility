import pandas as pd
import configparser
from pathlib import Path
import logging
from logger import setup_logger, format_func_msg
from utils import LOG_PATH


logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

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


def validate_data(file_type: str,
                  data_file: str | Path,
                  logger: logging.Logger = logger) -> dict:
    """驗證資料是否符合模板，並回傳驗證結果。
    
    Args:
        file_type: 表種
        data_file: 資料檔案路徑
        logger: 日誌記錄器
    Returns:
        dict: 驗證結果
    """
    # 可以放在utils.py
    template_file = f"./data/std_template/增辦第4期-{file_type}.xlsx"
    

    try:
        if file_type == "表單9":
            template_columns = load_complex_schema(path=template_file)[:20]
            data_columns = load_complex_schema(path=data_file)[:20]
        else:
            template_columns = load_complex_schema(path=template_file)[:14]
            data_columns = load_complex_schema(path=data_file)[:14]
    except Exception as e:
        logger.error(
            format_func_msg(func='validate_data', msg=f"讀取 schema 時發生錯誤: {e}"))
        return {
            "status": {
                "status": "False",
                "message": f"❌ 讀取欄位結構失敗！錯誤訊息: {str(e)}"
            },
            "sub_status": {
                "entity_code": {
                    "status": "False",
                    "message": "❌ 無法驗證業者代碼！"
                },
                "column_name": {
                    "status": "False",
                    "message": "❌ 無法驗證欄位名稱！"
                }
            }
        }

    logger.info(format_func_msg(func='validate_data', msg="開始驗證資料..."))

    validation_passed = True
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
            error_columns.append(col_2)

    if error_columns:
        error_msg = f"資料中與模板中不一致的欄位: {error_columns}"
        logger.error(format_func_msg(func='validate_data', msg=error_msg))
        error_messages.append(error_msg)
        validation_passed = False

    logger.info(
        format_func_msg(func='validate_data',
                        msg=f"驗證完成，結果: {'通過' if validation_passed else '失敗'}"))

    # 返回結果結構
    if validation_passed:
        return {
            "status": {
                "status": "True",
                "message": "✅ 欄位結構正確"
            },
            "sub_status": {
                "entity_code": {
                    "status": "True",
                    "message": "✅ 業者代碼正確"
                },
                "column_name": {
                    "status": "True",
                    "message": "✅ 欄位名稱及順序正確"
                }
            }
        }
    else:
        return {
            "status": {
                "status": "False",
                "message": f"❌ 欄位結構錯誤！錯誤訊息: {'; '.join(error_messages)}"
            },
            "sub_status": {
                "entity_code": {
                    "status": "False",
                    "message": "❌ 業者代碼錯誤！"
                },
                "column_name": {
                    "status": "False",
                    "message": f"❌ 欄位名稱錯誤！錯誤欄位: {error_columns}"
                }
            }
        }