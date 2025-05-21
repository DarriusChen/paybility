from pathlib import Path


import pandas as pd
import json
import re

class PathValidator:
    def __init__(self, args):
        # params
        self.args = args
        self.path = args.filepath
        # normalize path
        self.abspath = Path(self.path).resolve()
        
        self.period = None
        self.year = None
        self.county = None
        self.month = None
        
        self.info = {}
        # func
        # print("Parent Path Checking...")
        self.parent_path_check()
        # print("File Checking...")
        self.file_name_check()
        self.file_test()
        
    def parent_path_check(self):
        
        
        parts = list(self.abspath.parts)
        # print(parts)
        if len(parts) < 5:
            # print("父層資料夾數不足")
            self.info["Path"] = "❌ 路徑錯誤"
        else:
            for i in range(len(parts)-4):
                # print(parts[i:i+4])
                period, year, county, month = parts[i:i+4]
                
                
                if (re.fullmatch(r"\d+期", period) and
                    re.fullmatch(r"\d{3}年", year) and
                    re.fullmatch(r".{2}", county) and
                    re.fullmatch(r"\d{1,2}月", month)):
                    pathinfo = {}
                    # print(period, year, county, month)
                    if self.is_valid_period(period):
                        pathinfo["期"] = period
                    else:
                        pathinfo["期"] = None
                    if self.is_valid_year(year):
                        pathinfo["年"] = year
                    else:
                        pathinfo["年"] = None
                        
                    if self.is_valid_county(county):
                        pathinfo["縣市"] = county
                    else:
                        pathinfo["縣市"] = None
                        
                    if self.is_valid_month(month):
                        pathinfo["月"] = month
                    else:
                        pathinfo["月"] = None
                        
                    # print(pathinfo)
                
                
        if None in pathinfo.values():    
            # print("❌ 路徑錯誤")
            self.info["Path"] = "❌ 路徑錯誤"
        else: 
            # print("✅ 路徑正確")
            self.info["Path"] = "✅ 路徑正確"
            self.info["Path_info"] = pathinfo
    
    def file_test(self):
        file_info = {}
        # suffix check
        if self.abspath.suffix not in [".xlsx", ".xls"]:
            # "副檔名錯誤：{self.abspath.name} 不是 Excel 檔案 (.xlsx/.xls)"
            file_info["Suffix"] = "❌ 副檔名錯誤"
        else:
            file_info["Suffix"] = self.abspath.suffix
        
        # file exist check 
        if not self.abspath.exists():

            file_info["Status"] = "❌ 找不到檔案"
        else:
            file_info["Status"] = "✅ 檔案存在"
        # load file
        try:
            df = pd.read_excel(self.abspath, header=None)
            file_info["Load"] = "✅ 讀取成功"
            # print(f"✅ 成功讀取 Excel 檔案：{path.name}")
            
        except FileNotFoundError:
            file_info["Load"] = "❌ 檔案不存在！"
         
        except Exception as e:
            file_info["Load"] = f"❌ 讀取失敗：{e}"
        
        self.info["File"] = file_info

    def file_name_check(self, company_code=""):
        file_name_info = {}
        
        # table name check
        for table_name in self.args.tables:
            
            if table_name in self.abspath.name:
                file_name_info["Table"] = table_name
                break
            else:
                file_name_info["Table"] = None
        
        # Todo company code check
        # if company_code in self.abspath.name:
        #     file_name_info["Company Code"] = company_code
        # else: 
        file_name_info["Company_code"] = None
        
        self.info["File_name"] = file_name_info
        
    def get_info(self):
        return self.info
    
    def show_info(self):
        print(json.dumps(self.info, indent=4, ensure_ascii=False))
        
    def is_valid_period(self, period):
        # period check

        if period[:-1] not in self.args.period:        
            # "❌ 期別錯誤"
            return False
        else:
            # "✅ 期別正確"
            self.period = period
            return True
    
    def is_valid_year(self, year):
        # year check
        if self.is_int(year[:-1]):
            if self.args.minyear <= int(year[:-1]) <= self.args.maxyear:
                # "✅ 年限正確"
                self.year = year
                return True
            else:
                # "❌ 年限錯誤"
                return False
        else:
            # "❌ 年限須為羅馬數字"
            return False
    
    def is_valid_county(self, county):
         # county check
        if county in self.args.county:
            self.county = county
            return True, "✅ 縣市正確"
        else :
            return False, "❌ 縣市錯誤"
    
    def is_valid_month(self, month):
        # month check
        
        if self.is_int(month[:-1]):
            if 1 <= int(month[:-1]) <= 12:
                # "✅ 月份正確"
                self.month = month
                
                return True
            else:
                # "❌ 月份錯誤"
                return False
        else:
            # "❌ 月份須為羅馬數字"
            return False
        
    def is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False
        