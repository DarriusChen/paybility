import test_streamlit as st
import json
import pandas as pd
from utils.utils import RESULT_PATH

# 用 session_state 儲存日誌，避免每次重新執行就消失
if "log_lines" not in st.session_state:
    st.session_state.log_lines = []

if 'show_result' not in st.session_state:
    st.session_state.show_result = False

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

# TODO: 改成實際的結果 (result_obj)
def streamlit_app(result_path: str = RESULT_PATH):
    st.title("📁 自動付款清冊系統")
    st.write("請上傳 Excel 檔案，系統將自動進行驗證")
    files = st.file_uploader("上傳檔案", type=["xlsx", "xls"], accept_multiple_files=True, label_visibility="collapsed")
    if files:
        st.success("上傳成功! 共上傳 {} 個檔案".format(len(files)))
        st.button("開始驗證", on_click=test_validate_file, args=(files,), key="validate_button")
    else:
        st.warning("請上傳檔案")
    
    if st.session_state.show_result:
        st.button("關閉結果", on_click=close_result, key="close_result_button")
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