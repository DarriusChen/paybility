import pyodbc
import os
from typing import List, Dict
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

class DatabaseService:
    def __init__(self):
        # pyodbc 連接設定 (用於存儲過程和複雜查詢)
        self.driver = "{ODBC Driver 18 for SQL Server}"
        self.server = config["database"]["host"]
        self.user = config["database"]["user"]
        self.pwd = config["database"]["password"]
        self.db_name = config["database"]["database"]
        self.connection_string = (
            f"DRIVER={self.driver};SERVER={self.server};"
            f"DATABASE={self.db_name};UID={self.user};PWD={self.pwd};"
            "TrustServerCertificate=yes;Encrypt=yes;"
        )

    def get_pyodbc_connection(self):
        """取得 pyodbc 連接 """
        return pyodbc.connect(self.connection_string)
    
    def get_data(self, table_name: str, column_name: str = None, value: str = None) -> List[Dict]:
        """使用 pyodbc 取得資料"""
        conn = self.get_pyodbc_connection()
        try:
            cursor = conn.cursor()
            if column_name and value:
                cursor.execute(f"SELECT * FROM {table_name} WHERE {column_name} = ?", value)
            elif column_name:
                cursor.execute(f"SELECT * FROM {table_name} WHERE {column_name}")
            else:
                cursor.execute(f"SELECT * FROM {table_name}")
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results, len(results)
        finally:
            conn.close()

    def get_data_by_match_id(self, match_id: str, table_name: str) -> List[Dict]:
        """使用 pyodbc 取得對應媒合編號資料"""
        conn = self.get_pyodbc_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE 媒合編號 = ?", match_id)
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        finally:
            conn.close()