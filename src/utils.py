import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Path Parameter
MAX_YEAR = int(config['path_parameter']['max_year'])
MIN_YEAR = int(config['path_parameter']['min_year'])
PERIOD = config.get('path_parameter', 'period').split(',')
COUNTY = config.get('path_parameter', 'county').split(',')
TABLES = config.get('path_parameter', 'tables').split(',')
# Path Config
RESULT_PATH = config['output_path']['result_path']
LOG_PATH = config['output_path']['log_path']

# print(MAX_YEAR, MIN_TEAR, PERIOD, COUNTY, TABLES)

#  result template
def attribute():
    return {"status": False, "info": None, "message": ""}

def get_dict_template(name: str):
    """回傳result模板

    Args:
        name (str): 模板名稱:
            'path_check', 'file_check', 'filename_check', 'schema_check'

    Returns:
        dict: result模板
    """
    template = {"status": attribute()}
    
    if name == "path_check":
        sub_status = {
            "period": attribute(),
            "county": attribute(),
            "year": attribute(),
            "month": attribute()
        }
        template["sub_status"] = sub_status
    elif name == "file_check":
        sub_status = {
            "suffix": attribute(),
            "exist": attribute(),
            "readable": attribute()
        }
        template["sub_status"] = sub_status
    elif name == "filename_check":
        sub_status = {
            "table":attribute(),
            "companycode": attribute()
            
        }
        template["sub_status"] = sub_status
    elif name == "schema_check":
        sub_status = {

        }
        template["sub_status"] = sub_status
    else:
        return None
    return template
    