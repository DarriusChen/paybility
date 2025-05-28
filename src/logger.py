import logging
from typing import Optional
import os

def setup_logger(name: str,
                 level: int = logging.INFO,
                 file_path: Optional[str] = None) -> logging.Logger:
    """設定 logger。
    
    Args:
        name: logger 名稱，建議使用 __name__
        level: 日誌級別
        file_path: 日誌文件路徑，如果為 None 則只輸出到控制台
    
    Returns:
        logging.Logger: 配置好的 logger 實例
    """
    logger = logging.getLogger(name)

    # 避免重複添加 handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(lineno)d | %(message)s'
    )

    if file_path:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            pass

    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def format_func_msg(func: str, msg: str) -> str:
    """格式化函式訊息。
    
    Args:
        func: 函式名稱
        msg: 訊息內容
    
    Returns:
        str: 格式化後的訊息
    """
    return f"{func} : {msg}"
