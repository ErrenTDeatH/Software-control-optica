import sqlite3
import json
import os

db_path = r"c:\Users\Antho\Software control optica\optica.db"
output_path = r"c:\Users\Antho\Happy app\local_inventory_export.json"

if not os.path.exists(db_path):
    print(f"Error: {db_path} no existe")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener columnas
        cursor.execute("PRAGMA table_info(inventario)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Obtener datos
        cursor.execute("SELECT * FROM inventario")
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
            
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            
        print(f"Éxito: Se exportaron {len(data)} productos a {output_path}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
