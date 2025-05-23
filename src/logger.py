import logging

def setup_logger(name: str,
                 level: int = logging.INFO,
                 file_path: str|None = None) -> logging.Logger:
    """設定 logger。"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if file_path:
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger