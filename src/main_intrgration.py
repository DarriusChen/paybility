import streamlit as st
import json
import pandas as pd
from utils.utils import RESULT_PATH
import uuid
from database import DatabaseService

from result import Result
from file_validator import validate_path
from schema_validator import validate_schema
from logic_validator import validate_logic


# 用 session_state 儲存日誌，避免每次重新執行就消失
if "log_lines" not in st.session_state:
    st.session_state.log_lines = []

# if "attribute" not in st.session_state:
#     st.session_state.log_lines = {}

if 'show_result' not in st.session_state:
    st.session_state.show_result = False

if "file_uploader" not in st.session_state:
    st.session_state.file_uploader = str(uuid.uuid4())

if "database_service" not in st.session_state:
    st.session_state.database_service = DatabaseService()



# Test function


# TODO: 改成實際的驗證函數
def test_validate_file(files, result_path):
    st.session_state.show_result = True
    st.session_state.log_lines.append("=== 驗證開始 ===")
    for i, file in enumerate(files):
        st.session_state.log_lines.append(f"[{i+1}/{len(files)}]上傳檔案: {file.name}")
        # st.session_state.log_lines.append(f"檔案類型: {file.type}")
        # st.session_state.log_lines.append(f"檔案大小: {file.size} bytes")
        result_obj = Result(file_name=file.name, result_path=result_path)
        
        file_check_result = validate_path(file)
        if file_check_result["status"]["status"]:
            st.session_state.log_lines.append("--- ✅檔名 ---")
            result_obj.update_result('file_check', file_check_result)
            

            # parameters
            data_frame = file_check_result["sub_status"]["readable"]["info"]
            file_type = file_check_result["sub_status"]["name"]["info"]["A"]
            county = file_check_result["sub_status"]["company_info"]["info"]["縣市"]
            county_code = file_check_result["sub_status"]["company_info"]["info"]["縣市代碼"]
            company_code = file_check_result["sub_status"]["company_info"]["info"]["系統業者代號"]
            period = file_check_result["sub_status"]["name"]["info"]["C"]

            # ------------------------------
            schema_result = validate_schema(data_file=data_frame,
                                    file_type=file_type,           
                                    company_code=company_code)
            result_obj.update_result('schema_check', schema_result)

            if schema_result["status"]["status"]:
                st.session_state.log_lines.append("--- ✅表頭 ---")
            else:
                st.session_state.log_lines.append("--- ❌表頭 ---")

            # ------------------------------
            logic_result = validate_logic( data_frame,
                                    file_type=file_type,
                                    phase=period,
                                    county=county,
                                    county_code=county_code)
            result_obj.update_result('logic_check', logic_result)
            
            if schema_result["status"]["status"]:
                st.session_state.log_lines.append("--- ✅業務邏輯 ---")
            else:
                st.session_state.log_lines.append("--- ❌業務邏輯 ---")

        else:
            st.session_state.log_lines.append("--- ❌檔名 ---")
            # st.session_state.log_lines.append(f"{file_check_result['sub_status']}")
            

        result_obj.save_result()

    
        
        



    st.session_state.log_lines.append("=== 驗證完成 ===")

def close_result():
    st.session_state.show_result = False

def restart_app():
    st.session_state.log_lines = []
    st.session_state.show_result = False

    # 清掉 uploader 的內容
    st.session_state.file_uploader = str(uuid.uuid4())

# TODO: 改成實際的結果 (result_obj)
def streamlit_app(result_path: str = RESULT_PATH):
    st.title("📁 自動付款清冊系統")
    st.write("---")
    st.write("請上傳 Excel 檔案，系統將自動進行驗證")

    

    files = st.file_uploader("上傳檔案", type=["xlsx", "xls"], key=st.session_state.file_uploader, accept_multiple_files=True, label_visibility="collapsed")

    left, middle, right = st.columns(3)

    if files:
        st.success("上傳成功! 共上傳 {} 個檔案".format(len(files)))
        with left:
            st.button("開始驗證", on_click=test_validate_file, args=(files, result_path), key="validate_button", icon="➡️",  use_container_width=True)
        with right:
            st.button("重新驗證", on_click=restart_app, key="restart_button", icon="🔄", use_container_width=True)
    else:
        st.warning("請上傳檔案")
    
    if st.session_state.show_result:
        st.button("關閉結果", on_click=close_result, key="close_result_button", icon="❌")
        with st.container(height=900, border=True):
            # with open(result_path, "r") as f:
                # result = json.load(f)
                # st.write(result)
    #             df = pd.json_normalize(result)
    #             st.dataframe(df)
    #         # for 測試用，只顯示最後 100 行，避免資料量過大
            for line in st.session_state.log_lines[-100:]:
                st.write(line)
    

# ------------------------------------------------------------#

def search_page():
    st.title("🔍 搜尋已上傳檔案")
    st.write("---")
    st.write("請使用查詢條件或關鍵字搜尋")
    st.write("\n")
    left, middle, right = st.columns(3)
    with left:
        st.selectbox("期別", ["2", "3", "31", "41"], key="period")
    with middle:
        st.selectbox("表種", ["表4", "表7", "表9"], key="table_type")
    with right:
        st.selectbox("縣市", ["臺北", "臺中", "臺南", "高雄", "基隆", "新竹", "嘉義", "新北", "宜蘭", "桃園", "新竹", "苗栗", "彰化", "南投", "雲林", "嘉義", "屏東", "宜蘭", "花蓮", "臺東", "澎湖", "金門", "連江"], key="city")
    search_query = st.text_input(label="關鍵字搜尋", placeholder="請輸入要搜尋的關鍵字")
    if st.button("搜尋"):
        st.write(f"搜尋結果: {search_query}")
        st.write(st.session_state.period, st.session_state.table_type, st.session_state.city)

# ------------------------------------------------------------#

def search_database():
    st.title("🔍 資料庫查詢")
    st.write("---")
    left, middle, right = st.columns(3)

    db = st.session_state.database_service

    with left:
        st.text_input(label="資料表名稱", key="table_name")
    with middle:
        st.text_input(label="資料表欄位", key="column_name")
    with right:
        st.text_input(label="資料表欄位值", key="value")
    if st.button("搜尋"):
        result, count = db.get_data(st.session_state.table_name, st.session_state.column_name, st.session_state.value)
        st.write(f"搜尋結果: 共 {count} 筆資料")
        st.write(result)

# ------------------------------------------------------------#

if __name__ == "__main__":
    page_names_to_funcs = {
        "Home": streamlit_app,
        "Search": search_page,
        "Search Database": search_database,
    }
    page_name = st.sidebar.selectbox("選擇頁面", page_names_to_funcs.keys())
    page_names_to_funcs[page_name]()
