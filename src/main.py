import argparse
from file_validator import validate_path

from logger import setup_logger, format_func_msg
from schema_validator import validate_schema
from logic_validator import validate_matching_numbers
from result import Result
# config
from utils.utils import RESULT_PATH, LOG_PATH, MAPPING_FILE

logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

parser = argparse.ArgumentParser(description='Paybility')

parser.add_argument('filepath', type=str, help='.xls path')

def main(args):
    
    # 創建 Result object
    result_obj = Result(file_name=args.filepath, result_path=RESULT_PATH)
    
    # Step 1: file check
    # pv = PathValidator(args) # TODO: 傳入 result_obj
    path_check_result, file_check_result, filename_check_result = validate_path(args.filepath)
    
    # 更新 File level 檢查結果
    # update path_check
    if result_obj.update_result('path_check', path_check_result):
        logger.info(format_func_msg(func='main', msg="Path 檢查結果更新成功"))
    else:
        logger.error(format_func_msg(func='main', msg="Path 檢查結果更新失敗"))
        
    # update file_check
    if result_obj.update_result('file_check', file_check_result):
        logger.info(format_func_msg(func='main', msg="File 檢查結果更新成功"))
    else:
        logger.error(format_func_msg(func='main', msg="File 檢查結果更新失敗"))
        
    # update filename_check
    if result_obj.update_result('filename_check', filename_check_result):
        logger.info(format_func_msg(func='main', msg="File Name 檢查結果更新成功"))
    else:
        logger.error(format_func_msg(func='main', msg="File Name 檢查結果更新失敗"))

    # ------------------------------------------------------------ #
    
    # Step 2: schema check
    file_type = filename_check_result["sub_status"]["table"]["info"]
    county = path_check_result["sub_status"]["county"]["info"]
    schema_result = validate_schema(file_type=file_type,
                                    data_file=args.filepath,
                                    county=county)
    
    # 更新 Schema 檢查結果
    if result_obj.update_result('schema_check', schema_result):
        logger.info(format_func_msg(func='main', msg="Schema 檢查結果更新成功"))
    else:
        logger.error(format_func_msg(func='main', msg="Schema 檢查結果更新失敗"))

    # ------------------------------------------------------------ #
    # Step 3: logic check -1: 媒合編號
    period = path_check_result["sub_status"]["period"]["info"]
    logic_result_matching_numbers = validate_matching_numbers(
                                            data_file=args.filepath,
                                            logger=logger,
                                            county=county,
                                            phase=period)
    if result_obj.update_result('logic_check_matching_numbers', logic_result_matching_numbers):
        logger.info(format_func_msg(func='main', msg="媒合編號 檢查結果更新成功"))
    else:
        logger.error(format_func_msg(func='main', msg="媒合編號 檢查結果更新失敗"))

    # Step 4: 

    # ------------------------------------------------------------ #
     
    # Last Step: 保存最終結果
    if result_obj.save_result():
        logger.info(format_func_msg(func='main', msg="驗證結果已成功保存"))
    else:
        logger.error(format_func_msg(func='main', msg="驗證結果保存失敗"))

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)