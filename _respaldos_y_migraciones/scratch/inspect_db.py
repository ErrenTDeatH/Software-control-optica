import sqlite3
import os

db_path = r"c:\Users\Antho\Software control optica\optica.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} no existe")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tablas encontradas: {tables}")
        
        for table in tables:
            name = table[0]
            cursor.execute(f"SELECT count(*) FROM {name}")
            count = cursor.fetchone()[0]
            print(f"  - {name}: {count} registros")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
