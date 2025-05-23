import pandas as pd
from pathlib import Path
from logger import setup_logger

def load_complex_schema(path: str|Path,
                        is_template: bool = True,
                        header_rows: list[int] = [2, 3],
                        sheet: int = 0) -> list[str]:
    """讀取雙層表頭並攤平成單層欄位。
    
    Args:
        path: 檔案路徑
        is_template: 是否為模板
        header_rows: 表頭行數
        sheet: 工作表索引
        
    Returns:
        pd.DataFrame: 攤平後的 DataFrame
    """
    df = pd.read_excel(path, sheet_name=sheet, header=header_rows)

    # → flatten MultiIndex columns and remove \n
    df.columns = [
        '_'.join(str(c).strip().replace('\n', '') for c in col if str(c) != 'nan')
        for col in df.columns.values
    ]

    return df.columns.tolist()

def validate_data(template_file: str|Path,
                  data_file: str|Path) -> bool:
    """驗證資料是否符合模板。
    
    Args:
        template_file: 模板檔案路徑
        data_file: 資料檔案路徑
        
    Returns:
        bool: 驗證結果
    """

    result = True
    
    logger = setup_logger(name='schema_validator',
                          file_path='schema_validator.log')
    
    try:
        template_columns = load_complex_schema(path=template_file, is_template=True)
        data_columns = load_complex_schema(path=data_file, is_template=False)
    except Exception as e:
        logger.error(f"讀取檔案時發生錯誤: {e}")
        return None
    
    # 驗證欄位數量是否符合模板
    template_columns_len = len(template_columns)
    data_columns_len = len(data_columns)
    if template_columns_len != data_columns_len:
        logger.error(f"資料欄位數量與模板不符: "
                     f"template: {len(template_columns)}, "
                     f"data: {len(data_columns)}")
        result = False
    
    # 驗證欄位名稱是否符合模板
    error_columns = []
    compare_columns = {template_columns_len: template_columns, data_columns_len: data_columns}

    # 如果欄位數量不符，則補齊空欄位，使兩者欄位數量相同
    if template_columns_len != data_columns_len:
        difference_columns = max(template_columns_len, data_columns_len) - min(template_columns_len, data_columns_len)
        shorter_columns = compare_columns[min(template_columns_len, data_columns_len)]
        shorter_columns_len = len(shorter_columns)
        columns_padding = [""] * difference_columns
        shorter_columns.extend(columns_padding)
        compare_columns[shorter_columns_len] = shorter_columns

    for col_1, col_2 in zip(compare_columns[template_columns_len], compare_columns[data_columns_len]):
        if col_1 != col_2:
            error_columns.append(col_2)
    
    if error_columns:
        logger.error(f"資料中與模板中不一致的欄位: {error_columns}")
        result = False
    
    return result








    
    