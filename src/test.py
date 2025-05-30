from pathlib import Path

import subprocess
import json
import os

def contains_none(d):
    if (d["Path"] == None or d["File_name"]["Table"] == None or
        d["Path_info"]["期"] == None or d["Path_info"]["年"] == None or 
        d["Path_info"]["縣市"] == None or d["Path_info"]["月"] == None):
        return True
        
        
root_path = Path("data").resolve()
# print(root_path)

total = 0
correct = 0
error = 0


    
for path in root_path.rglob("*"):
    
    
    if path.is_file():
        total += 1
        
        print(f"\n🚀 測試案例{total}：{path.name}")
        # try:
        result = subprocess.run(["python", "src/main.py", path],
                                capture_output=True, text=True)
        # print("📤 stdout:\n", )
        print(result.stdout)
        # result_dict = dict(json.loads(result.stdout))
        # try:
        #     if contains_none(result_dict):
        #         error += 1
        #         print(result_dict)
        #     else:
        #         correct += 1
        # except Exception as e:
        #     print(f"💥 執行錯誤：{e}")
        #     print(result_dict)

print(f"{correct}/{total}")


        