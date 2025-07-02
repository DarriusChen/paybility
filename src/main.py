import argparse
from file_validator import validate_path

from logger import setup_logger, format_func_msg
from schema_validator import validate_schema
from logic_validator import validate_logic
from result import Result
# config
from utils.utils import RESULT_PATH, LOG_PATH, MAPPING_FILE

logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

parser = argparse.ArgumentParser(description='Paybility')

parser.add_argument('filepath', type=str, help='.xls path')

def main(args):
    
    # Todo: 以下這些之後定案可以統整成一個dict
    # file_type = file_check_result["sub_status"]["name"]["info"]["A"]
    # # Todo 換成UI上選擇的結果
    # county = file_check_result["sub_status"]["company_info"]["info"]["縣市"]
    # company_code = file_check_result["sub_status"]["company_info"]["info"]["系統業者代號"]

    # 創建 Result object
    result_obj = Result(file_name=args.filepath, result_path=RESULT_PATH)
    # Step 1: file check
    file_check_result = validate_path(args.filepath)

    # update file_check
    if result_obj.update_result('file_check', file_check_result):
        logger.info(format_func_msg(func='main', msg="File 檢查結果更新成功"))
    else:
        logger.error(format_func_msg(func='main', msg="File 檢查結果更新失敗"))
    # 檔案名稱要對才能繼續往下...
    # ------------------------------------------------------------ #
    # print(file_check_result["sub_status"]["company_info"]["info"]["縣市"])
    # Step 2: schema check
    file_type = file_check_result["sub_status"]["name"]["info"]["A"]
    # Todo 換成UI上選擇的結果
    county = file_check_result["sub_status"]["company_info"]["info"]["縣市"]
    company_code = file_check_result["sub_status"]["company_info"]["info"]["系統業者代號"]
    schema_result = validate_schema(file_type=file_type,
                                    data_file=args.filepath,
                                    county=county,
                                    company_code=company_code)
    
    # 更新 Schema 檢查結果
    if result_obj.update_result('schema_check', schema_result):
        logger.info(format_func_msg(func='main', msg="Schema 檢查結果更新成功"))
    else:
        logger.error(format_func_msg(func='main', msg="Schema 檢查結果更新失敗"))

    # ------------------------------------------------------------ #
    # Step 3: logic check -1: 媒合編號
    period = file_check_result["sub_status"]["name"]["info"]["C"]
    logic_result = validate_logic(
                                    data_file=args.filepath,
                                    logger=logger,
                                    # county=county,
                                    tabletype=file_type,
                                    phase=period)
    if result_obj.update_result('logic_check', logic_result):
        logger.info(format_func_msg(func='main', msg="媒合編號 檢查結果更新成功"))
    else:
        logger.error(format_func_msg(func='main', msg="媒合編號 檢查結果更新失敗"))

    


    # ------------------------------------------------------------ #
    # Step 4:  



    # Last Step: 保存最終結果
    if result_obj.save_result():
        logger.info(format_func_msg(func='main', msg="驗證結果已成功保存"))
    else:
        logger.error(format_func_msg(func='main', msg="驗證結果保存失敗"))

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)