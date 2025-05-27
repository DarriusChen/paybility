import argparse
import configparser

from file_validator import PathValidator

from logger import setup_logger, format_func_msg
from schema_validator import validate_data
from result import Result

config = configparser.ConfigParser()
config.read('config.ini')
result_path = config['result_path']['path']

logger = setup_logger(name=__name__, file_path=f'../output/logs/{__name__}.log')

parser = argparse.ArgumentParser(description='Paybility')

parser.add_argument('filepath', type=str, help='.xls path')
parser.add_argument('--maxyear', type=int, help='最大民國年限', default=150)
parser.add_argument('--minyear', type=int, help='最小民國年限', default=0)
parser.add_argument('--period', type=list, help='期別', default=['2', '3', '31', '4', '41', '5'])
parser.add_argument('--county', type=list, help='縣市', default=['台北', '新北', '桃園', '台中', '台南', '高雄', '彰化', '南投'])
parser.add_argument('--tables', type=list, help='表種', default=['表4', '表7', '表9', '表單4', '表單7', '表單9'])

def main(args):
    
    # 創建 Result object
    result_obj = Result(file=args.filepath, result_path=result_path)
    
    # Step 1: file check
    pv = PathValidator(args) # TODO: 傳入 result_obj
    info = pv.show_info()
    file_type = info['File_name']["Table"]
    # file_check_result = pv.show_result() # TODO: 用result.py 更新result
    
    # 更新 File level 檢查結果
    # if result_obj.update_result('file_check', file_check_result["result"]["file_check"]):
    #     logger.info(format_func_msg(func='main', msg="文件檢查結果更新成功"))
    # else:
    #     logger.error(format_func_msg(func='main', msg="文件檢查結果更新失敗"))

    # ------------------------------------------------------------ #
    
    # Step 2: schema check
    schema_result = validate_data(
        file_type=file_type,
        data_file=args.filepath,
    )
    
    # 更新 Schema 檢查結果
    if result_obj.update_result('schema_check', schema_result):
        logger.info(format_func_msg(func='main', msg="Schema 檢查結果更新成功"))
    else:
        logger.error(format_func_msg(func='main', msg="Schema 檢查結果更新失敗"))

    # ------------------------------------------------------------ #
     
    # Last Step: 保存最終結果
    if result_obj.save_result():
        logger.info(format_func_msg(func='main', msg="驗證結果已成功保存"))
    else:
        logger.error(format_func_msg(func='main', msg="驗證結果保存失敗"))

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)