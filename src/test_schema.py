import configparser
from schema_validator import validate_schema
from result import Result

config = configparser.ConfigParser()
config.read('config.ini')
result_path = config['output_path']['result_path']
log_path = config['output_path']['log_path']

data_file = "./data/41期/114年/台北/3月/易居-41期-11403/表9_易居41期業者服務補助費用清冊_11403 - 修.xlsx"

file_name = data_file.split('/')[-1]

result_obj = Result(file_name=file_name, result_path=result_path)


if __name__ == "__main__":
    result = validate_schema(
        file_type="表9",
        data_file=data_file,
        county="台北市")
    result_obj.update_result('schema_check', result)
    result_obj.save_result()
