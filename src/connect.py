import sqlite3

# 建立或連線到資料庫
conn = sqlite3.connect("./test.db")

# 建立 cursor 物件
cursor = conn.cursor()

# 建立一個表格
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER
    )
''')

# 提交變更
conn.commit()

# 關閉連線
conn.close()

def create():
    pass

def insert():
    pass

def select():
    pass

def remove():
    pass

def update():
    pass