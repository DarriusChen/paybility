import json
from pathlib import Path
from typing import Dict, Any
from configparser import ConfigParser
from logger import setup_logger, format_func_msg
from utils import get_dict_template

config = ConfigParser()
config.read('config.ini')
result_path = config['output_path']['result_path']
log_path = config['output_path']['log_path']

logger = setup_logger(name=__name__, file_path=f'{log_path}/{__name__}.log')

class Result:
    def __init__(self,
                 file_name: str|Path,
                 result_path: str|Path = result_path):
        self.fname = file_name
        self.result_path = result_path
        self.result = self._create_default_result()

    def _create_default_result(self) -> dict:
        """創建默認的結果結構。
        
        Returns:
            dict: 包含默認結果結構的字典
        """
        return {
            "name": self.fname,
            "result": {
                "path_check": get_dict_template("path_check"),
                "file_check": get_dict_template("file_check"),
                "filename_check": get_dict_template("filename_check"),
                "schema_check": get_dict_template("schema_check")
            }
        }

    def update_result(self, section: str, result_data: Dict[str, Any]) -> bool:
        """更新指定部分的驗證結果。
        
        Args:
            section: 要更新的部分 ('file_check' 或 'schema_check')
            result_data: 驗證結果數據
        
        Returns:
            bool: 是否成功更新結果
        """
        if section not in ['path_check', 'file_check', 'filename_check', 'schema_check']:
            logger.error(format_func_msg(func='update_result',
                                       msg=f"無效的 section: {section}"))
            return False

        try:
            self.result["result"][section] = result_data
            logger.info(format_func_msg(func='update_result',
                                      msg=f"{section} 結果更新成功"))
            return True
        except Exception as e:
            logger.error(format_func_msg(func='update_result',
                                       msg=f"更新 {section} 結果時發生錯誤: {e}"))
            return False

    def save_result(self) -> bool:
        """儲存驗證結果。
        
        Returns:
            bool: 是否成功保存結果
        """
        print(self.result)
        try:
            # 讀取現有結果
            try:
                with open(self.result_path, 'r') as f:
                    current_results = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                current_results = []

            # 添加新結果
            current_results.append(self.result)

            # 保存更新後的結果
            with open(self.result_path, 'w', encoding='utf-8') as f:
                json.dump(current_results, f, indent=4, ensure_ascii=False)

            logger.info(format_func_msg(func='save_result',
                                      msg=f"驗證結果已儲存至 {self.result_path}"))
            return True

        except Exception as e:
            logger.error(format_func_msg(func='save_result',
                                       msg=f"儲存驗證結果時發生錯誤: {e}"))
            return False
