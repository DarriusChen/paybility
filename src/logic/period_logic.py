from utils.utils import is_int

# 包租/轉租/代管期別邏輯

def valid_periodinfo(items: list):
    """檢查期別資訊是否正確
    
    Args:
        items:
    Returns:
        dict:
        
    """
    return {}

def check_period(period: str, total_period: str, period_type: str):
    
    """檢查期數是否正確 
    Args:
        period: 期數
        total_period: 總期數
        period_type: 包管/代管/轉租
    Returns:
        True/False
        
    """
    if is_int(period) and is_int(total_period):
        period = int(period)
        total_period = int(total_period)
        if period_type == "代管":
            if total_period == 12 and period < total_period : # 1Y
                return True, None, "O"
            else:
                return False, f"Wrong Period: {period} or Total Period {total_period}", "X"
        elif period_type == "包管":
            if total_period == 36 and period < total_period: # 3Y
                return True, None, "O"
            else:
                return False, f"Wrong Period: {period} or Total Period {total_period}", "X"
        elif period_type == "轉租":
            if total_period == 12 and period < total_period: # 1Y
                pass
            # 先不討論這個
            # else:
            return False, f"轉租", "X"
        else:
            return False, f"Wrong Period Type {total_period}", "X"
    
    return False, f"Wrong Period: {period} or Total Period {total_period}", "X"
