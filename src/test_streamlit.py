import streamlit as st
import json
import pandas as pd
from utils.utils import RESULT_PATH
import uuid

# 用 session_state 儲存日誌，避免每次重新執行就消失
if "log_lines" not in st.session_state:
    st.session_state.log_lines = []

if 'show_result' not in st.session_state:
    st.session_state.show_result = False

if "file_uploader" not in st.session_state:
    st.session_state.file_uploader = str(uuid.uuid4())

# Test function
# TODO: 改成實際的驗證函數
def test_validate_file(files):
    st.session_state.show_result = True
    st.session_state.log_lines.append("=== 驗證開始 ===")
    for file in files:
        st.session_state.log_lines.append(f"上傳檔案: {file.name}")
        st.session_state.log_lines.append(f"檔案類型: {file.type}")
        st.session_state.log_lines.append(f"檔案大小: {file.size} bytes")
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
    st.write("請上傳 Excel 檔案，系統將自動進行驗證")
    files = st.file_uploader("上傳檔案", type=["xlsx", "xls"], key=st.session_state.file_uploader, accept_multiple_files=True, label_visibility="collapsed")

    left, middle, right = st.columns(3)

    if files:
        st.success("上傳成功! 共上傳 {} 個檔案".format(len(files)))
        with left:
            st.button("開始驗證", on_click=test_validate_file, args=(files,), key="validate_button", icon="🔍",  use_container_width=True)
        with right:
            st.button("重新驗證", on_click=restart_app, key="restart_button", icon="🔄", use_container_width=True)
    else:
        st.warning("請上傳檔案")
    
    if st.session_state.show_result:
        st.button("關閉結果", on_click=close_result, key="close_result_button", icon="❌")
        with st.container(height=250, border=True):
            with open(result_path, "r") as f:
                result = json.load(f)
                df = pd.json_normalize(result)
                st.dataframe(df)
            # for 測試用，只顯示最後 100 行，避免資料量過大
            for line in st.session_state.log_lines[-100:]:
                st.write(line)

if __name__ == "__main__":
    streamlit_app()