import streamlit as st
import json
import pandas as pd
from utils.utils import RESULT_PATH
import uuid
from database import DatabaseService
import plotly.express as px

# 用 session_state 儲存日誌，避免每次重新執行就消失
if "log_lines" not in st.session_state:
    st.session_state.log_lines = []

if 'show_result' not in st.session_state:
    st.session_state.show_result = False

if "file_uploader" not in st.session_state:
    st.session_state.file_uploader = str(uuid.uuid4())

if "database_service" not in st.session_state:
    st.session_state.database_service = DatabaseService()

# Test function
# TODO: 改成實際的驗證函數
def test_validate_file(files):
    st.session_state.show_result = True
    # st.session_state.log_lines.append("=== 驗證開始 ===")
    # for file in files:
    #     st.session_state.log_lines.append(f"上傳檔案: {file.name}")
    #     st.session_state.log_lines.append(f"檔案類型: {file.type}")
    #     st.session_state.log_lines.append(f"檔案大小: {file.size} bytes")
    # st.session_state.log_lines.append("=== 驗證完成 ===")

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
            st.button("開始驗證", on_click=test_validate_file, args=(files,), key="validate_button", icon="➡️",  use_container_width=True)
        with right:
            st.button("重新驗證", on_click=restart_app, key="restart_button", icon="🔄", use_container_width=True)
    else:
        st.warning("請上傳檔案")
    
    if st.session_state.show_result:
        st.button("關閉結果", on_click=close_result, key="close_result_button", icon="✖")
        st.write("#### 驗證結果概覽：")
        with open(result_path, "r") as f:
            result = json.load(f)
            result_overview = []
            for item in result:
                result_overview.append({
                    "檔案名稱": item["file_name"],
                    "驗證結果": item["validate_result"]["message"]
                })
        with st.container(height=250, border=True):
            st.dataframe(pd.DataFrame(result_overview))

        validation_results = [item["驗證結果"] for item in result_overview]
        count_success = validation_results.count("✔")
        count_fail = validation_results.count("✖")
        count_df = pd.DataFrame([
            {"驗證結果": "驗證成功", "count": count_success},
            {"驗證結果": "驗證失敗", "count": count_fail}
        ])

        fig = px.pie(
            count_df, values="count", 
            names="驗證結果",
            color="驗證結果", color_discrete_map={"驗證成功": px.colors.qualitative.Set2[0], "驗證失敗": px.colors.qualitative.Set2[1]}, 
            hole=0.3,
        )
        st.plotly_chart(fig)
        st.write("---")

        # 詳細結果（針對驗證失敗）
        st.write("#### 驗證失敗說明：")
        for item in result:
            if item["validate_result"]["is_valid"] == False:
                with st.expander(item["file_name"]):
                    with st.container(border=True):
                        error_details = item["error_details"]
                        count = 1
                        for error_detail in error_details:
                            validate_item = list(error_detail.keys())[0]
                            st.write("---")
                            st.write(f"第 {count} 項檢查項目：", validate_item)
                            st.write(f"驗證結果：", error_detail[validate_item][0]["status"]["message"])
                            st.dataframe(pd.DataFrame(error_detail[validate_item][0]["sub_status"]), use_container_width=True)
                            count += 1
            # for 測試用，只顯示最後 100 行，避免資料量過大
            for line in st.session_state.log_lines[-100:]:
                st.write(line)

# ------------------------------------------------------------#

def search_page():
    st.title("🔍 搜尋已上傳檔案")
    st.write("---")
    st.write("請使用查詢條件或關鍵字搜尋")
    st.write("\n")

    db = st.session_state.database_service

    # 選單選項
    period_result, _ = db.get_data(table_name="Dim_Vendor", column_name="PLAN_CODE", unique_value=True)
    period_options = [result["PLAN_CODE"] for result in period_result]
    period_options.sort()
    county_result, _ = db.get_data(table_name="Dim_Vendor", column_name="COUNTY", unique_value=True)
    county_options = [result["COUNTY"] for result in county_result]
    county_options.sort()

    left, middle, right = st.columns(3)
    with left:
        st.selectbox("期別", period_options, key="period")
    with middle:
        st.selectbox("表種", ["表4", "表7", "表9"], key="table_type")
    with right:
        st.selectbox("縣市", county_options, key="city")
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
        if st.session_state.table_name:
            limit = 100
            result, count = db.get_data(st.session_state.table_name, st.session_state.column_name, st.session_state.value, limit=limit)
            real_data_count = db.get_data_count(st.session_state.table_name, st.session_state.column_name, st.session_state.value)
            st.write(f"搜尋結果: 共 {real_data_count} 筆資料（最多顯示前 {limit} 筆）")
            st.dataframe(result[:limit])
        else:
            st.warning("請輸入資料表名稱!")

# ------------------------------------------------------------#

if __name__ == "__main__":
    page_names_to_funcs = {
        "Home": streamlit_app,
        "Search": search_page,
        "Search Database": search_database,
    }
    page_name = st.sidebar.selectbox("選擇頁面", page_names_to_funcs.keys())
    page_names_to_funcs[page_name]()
