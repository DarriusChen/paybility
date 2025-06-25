import pandas as pd
import os
# from src.utils.utils import load_data

def get_matching_data(matching_number: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    取得匹配資料
    Args:
        matching_number: 匹配號碼
        dataframe: 表4、7、9 或 GS400 的資料
    Returns:
        pd.DataFrame: 匹配資料
    """
    # 取得匹配資料
    matching_data = dataframe[dataframe['媒合編號'] == matching_number]
    return matching_data


#TODO: 從資料庫取得匹配資料
def get_matching_data_from_database(matching_number: str) -> pd.DataFrame:
    """
    從資料庫取得匹配資料
    """
    
    pass