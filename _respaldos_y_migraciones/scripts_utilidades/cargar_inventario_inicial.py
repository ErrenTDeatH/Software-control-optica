"""
Script de carga de inventario inicial para Happy Vision.
Ejecutar UNA sola vez desde la carpeta del proyecto.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ No se encontraron las variables SUPABASE_URL y SUPABASE_KEY en el .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── Inventario extraído de la imagen ──────────────────────────────────────
INVENTARIO = [
    {"nombre": "Armazon TR90",           "categoria": "Monturas",   "marca": "COSTU",        "stock": 1,  "precio_costo": 4.62,  "precio_venta": 25.00, "sucursal": "Matriz"},
    {"nombre": "Armazon Acetato MAUROS", "categoria": "Monturas",   "marca": "MAUROS",       "stock": 1,  "precio_costo": 10.10, "precio_venta": 25.00, "sucursal": "Matriz"},
    {"nombre": "Armazon Acetato SEVEN",  "categoria": "Monturas",   "marca": "SEVEN VISION", "stock": 1,  "precio_costo": 8.50,  "precio_venta": 25.00, "sucursal": "Matriz"},
    {"nombre": "Pano de Microfibra",     "categoria": "Accesorios", "marca": "S/M",          "stock": 4,  "precio_costo": 0.81,  "precio_venta": 1.50,  "sucursal": "Matriz"},
    {"nombre": "Estuches Duros Normales","categoria": "Accesorios", "marca": "S/M",          "stock": 3,  "precio_costo": 2.60,  "precio_venta": 3.00,  "sucursal": "Matriz"},
    {"nombre": "Plaquetas Suaves",       "categoria": "Accesorios", "marca": "S/M",          "stock": 6,  "precio_costo": 3.13,  "precio_venta": 5.00,  "sucursal": "Matriz"},
    {"nombre": "Plaquetas Silicona",     "categoria": "Accesorios", "marca": "S/M",          "stock": 6,  "precio_costo": 2.09,  "precio_venta": 4.00,  "sucursal": "Matriz"},
    {"nombre": "Plaquetas Duras",        "categoria": "Accesorios", "marca": "S/M",          "stock": 6,  "precio_costo": 0.83,  "precio_venta": 3.00,  "sucursal": "Matriz"},
]

print(f"Cargando {len(INVENTARIO)} productos en Supabase (tabla: inventario)...")

errores = 0
for item in INVENTARIO:
    try:
        res = supabase.table("inventario").insert(item).execute()
        print(f"  OK: {item['nombre']}")
    except Exception as e:
        print(f"  ERROR en {item['nombre']}: {e}")
        errores += 1

print()
if errores == 0:
    print("Inventario cargado exitosamente! Ya puedes verlo en la app.")
else:
    print(f"Carga completada con {errores} errores.")
