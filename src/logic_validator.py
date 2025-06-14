from logic.logic1 import check_ID, is_account_vaild, is_valid_date, period_check

# Bank Account
print(is_account_vaild("252540118598"))

# ID Check
print(check_ID("F131000376"))
# Date Check
print(is_valid_date("2025/02/29"), is_valid_date("114/02/28"))

# Period Check
print(period_check("2", "36", "代管"))