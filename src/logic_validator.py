from pathlib import Path
import logging
from logger import setup_logger, format_func_msg
from utils import LOG_PATH, MAPPING_FILE, get_dict_template, load_data
import re

county_code_dict = {
    "台北市": "A",
    "新北市": "B",
    "桃園市": "C",
    "台中市": "D",
    "台南市": "E",
    "高雄市": "F",
}
# TODO: 縣市代碼資料庫

logger = setup_logger(name=__name__, file_path=f'{LOG_PATH}/{__name__}.log')

logic_result = get_dict_template("logic_check")

def is_valid_matching_number(matching_code: str, phase: str) -> list:
    """
    驗證媒合編號是否符合格式。
    
    Args:
        matching_code: 媒合編號
        phase: 計畫期別
    Returns:
        bool: 是否符合格式
    """
    errors = []

    pattern = r"^([\u4e00-\u9fff]{1,4})([A-F]{1})([12])(M)([123])(2|3|31|4|41)(\d{5})$"
    match = re.match(pattern, matching_code)

    if match:
        return None  # 完全符合格式
    else:
        # 詳細檢查每個部分
        # 1. 檢查業者名稱（1-4個中文字）
        dealer_pattern = r"^([\u4e00-\u9fff]{1,4})"
        dealer_match = re.match(dealer_pattern, matching_code)
        
        if not dealer_match:
            errors.append(f"業者名稱格式錯誤: {matching_code}。業者名稱須為1~4個中文字")
        
        dealer_name = dealer_match.group(1)
        remaining = matching_code[len(dealer_name):]

        # 2. 檢查縣市代號（A-F）
        if len(remaining) == 0:
            errors.append("縣市代碼開始出現缺漏！請檢媒合編號是否正確")
            return errors
        elif remaining[0] not in county_code_dict.values():
            errors.append(f"縣市代號缺漏或格式錯誤: {remaining[0]}。縣市代號須為 A-F")
        elif len(remaining) > 11 or len(remaining) < 10:
            errors.append(f"縣市代碼後長度不符: {remaining}！請檢查媒合編號是否正確")
        else:
            remaining = remaining[1:]

        # 3. 檢查縣市/公會版（1或2）
        if len(remaining) == 0:
            errors.append("縣市版／公會版代碼開始出現缺漏！請檢媒合編號是否正確")
            return errors
        elif remaining[0] not in '12':
            errors.append(f"縣市版或公會版代碼缺漏或格式錯誤: {remaining[0]}。縣市版或公會版代碼須為1或2")
        elif len(remaining) > 10 or len(remaining) < 9:
            errors.append(f"縣市版或公會版代碼後長度不符: {remaining}！請檢查媒合編號是否正確")
        else:
            remaining = remaining[1:]

        # 4. 檢查媒合編號類型（M）
        if len(remaining) == 0:
            errors.append("媒合編號類型開始出現缺漏！請檢媒合編號是否正確")
            return errors
        elif remaining[0] != 'M' or 'M' not in remaining:
            errors.append(f"媒合編號類型缺漏或格式錯誤: {remaining[0]}。媒合編號類型須為大寫M")
        elif len(remaining) > 9 or len(remaining) < 8:
            errors.append(f"媒合編號後長度不符: {remaining}！請檢查媒合編號是否正確")
        else:
            remaining = remaining[1:]

        # 5. 檢查契約類型（1、2或3）
        if len(remaining) == 0:
            errors.append("契約類型開始出現缺漏！請檢媒合編號是否正確")
            return errors
        elif remaining[0] not in '123':
            errors.append(f"契約類型缺漏或格式錯誤: {remaining[0]}。契約類型須為1、2或3")
        elif len(remaining) > 8 or len(remaining) < 7:
            errors.append(f"契約類型後長度不符: {remaining}！請檢查媒合編號是否正確")
        else:
            remaining = remaining[1:]

        # 6. 檢查計畫期別（2、3、31、4、41）
        if len(remaining) == 0:
            errors.append("計畫期別開始出現缺漏！請檢媒合編號是否正確")
            return errors
        elif remaining[:len(phase)] != phase:
            errors.append(f"計畫期別缺漏或格式錯誤: {remaining[:len(phase)]}。計畫期別須為{phase}")
        elif len(remaining) > 5 or len(remaining) < 5:
            errors.append(f"計畫期別後長度不符: {remaining}！請檢查媒合編號是否正確")
        else:
            remaining = remaining[len(phase):]

        # 7. 檢查流水號（5位數字）

        serial_pattern = r"^(\d{5})$"
        serial_match = re.match(serial_pattern, remaining)
        if not serial_match:
            if len(remaining) == 0:
                errors.append("流水號缺漏")
                return errors
            elif len(remaining) > 5 or len(remaining) < 5:
                errors.append(f"流水號長度不符(應為5位數字): {remaining}！請檢查媒合編號是否正確")
            else:
                errors.append(f"流水號格式錯誤(應為5位數字): {remaining}！請檢查媒合編號是否正確")

        return errors
    
        


def validate_matching_numbers(data_file: str | Path,
                             logger: logging.Logger,
                             phase: str) -> dict:
    """驗證媒合編號是否符合格式。
    
    Args:
        data_file: 資料檔案路徑
        phase: 計畫期別
    """
    try:
        df_matching_number = load_data(path=data_file,
                                       header_rows=[2, 3],
                                       logger=logger)
        matching_numbers = df_matching_number.iloc[:,0].dropna().to_list()
        errors = []
        for idx, number in enumerate(matching_numbers):
            error_result = is_valid_matching_number(number, phase)
            if error_result:
                errors.append(f"第{idx+1}筆: {number} 不符合格式")
        if not errors:
            logic_result['sub_status']['matching_number']['status'] = True
            logic_result['sub_status']['matching_number']['info'] = len(matching_numbers)
            logic_result['sub_status']['matching_number']['message'] = "✅ 媒合編號格式正確"
        else:
            logic_result['sub_status']['matching_number']['status'] = False
            logic_result['sub_status']['matching_number']['info'] = len(errors)
            logic_result['sub_status']['matching_number']['message'] = f"❌ 媒合編號格式錯誤: {errors}"

        return logic_result
    
    except Exception as e:
        logger.error(format_func_msg(func='validate_matching_numbers', msg=f"驗證媒合編號時發生錯誤: {e}"))
        return None
                