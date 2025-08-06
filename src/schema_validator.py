from utils.utils import TEMPLETE_PATH, load_schema, Result


# logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

def validate_schema(result: Result):
    """驗證資料是否符合模板，並回傳驗證結果。
    
    """

    result.set_checklevel("schema_validator")
    check_schema(result)
    
    result.update_status()


def check_schema(result: Result):

    file_type = result.get_info("表種")
    data_file = result.get_info("表格格式")

    template_file = f"{TEMPLETE_PATH}/增辦第4期-{file_type}.xlsx"

    if file_type == "表9":
        template_columns = load_schema(path=template_file)[:20]
        data_columns = data_file[:20]
    elif file_type == "表4" or file_type == "表7":
        template_columns = load_schema(path=template_file)[:14]
        data_columns = data_file[:14]

    # 驗證欄位數量是否符合模板
    template_columns_len = len(template_columns)
    data_columns_len = len(data_columns)
    if template_columns_len != data_columns_len:

        result.insert_error("表格格式", "資料欄位數量與模板不符")


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

        result.insert_error("表格格式", f"資料中與模板中不一致的欄位: {error_columns}")

