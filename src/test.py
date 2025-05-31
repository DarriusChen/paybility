from pathlib import Path

import subprocess
import json
import os

def contains_true(d: dict):
    for k, v in d["result"].items():
        # print(k, v["status"]["status"])
        if v["status"]["status"] == False:
            return False
    return True
        
def where_false(d: dict):
    for k, v in d["result"].items():
        # print(k, v["status"]["status"])
        if v["status"]["status"] == False:
            # print(v["sub_status"], type(v["sub_status"]))
            for k_, v_ in v["sub_status"].items():
                # if v_["status"] == False:
                print(k_, v_["message"])
            
           
root_path = Path("data\\41期").resolve()
# print(root_path)

total = 0
correct = 0
error = 0


    
for path in root_path.rglob("*"):
    
    
    if path.is_file():

        total += 1
        
        # print(f"\n🚀 {path}")
        # try:
        result = subprocess.run(["python", "src/main.py", path],
                                capture_output=True, text=True)
        # print(result.stdout)

        try:
            result_dict = dict(json.loads(result.stdout))
            if contains_true(result_dict):
                correct += 1
                
                # print("✅ 測試案例{total}：{path.name}")
            else:
                print(f"❌ 測試案例{total}：{path.name}")
                where_false(result_dict)
                error += 1
        except json.JSONDecodeError as e:
            print(f"❌ 測試案例{total}：{path.name}")
            where_false(result_dict)
            print("❌ JSON decode failed:", e)
            error += 1

print(f"{correct}/{total}")


        