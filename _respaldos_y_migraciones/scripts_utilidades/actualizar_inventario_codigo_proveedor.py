"""
Script para actualizar los registros con codigo_referencia y proveedor.
Ejecutar DESPUES de correr el SQL en Supabase para agregar las columnas.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Mapeo: nombre del producto -> (codigo_referencia, proveedor)
ACTUALIZACIONES = [
    ("Armazon TR90",            "COS9857",  "Imporlens S.A."),
    ("Armazon Acetato MAUROS",  "MA6988",   "Imporlens S.A."),
    ("Armazon Acetato SEVEN",   "VI703",    "Imporlens S.A."),
    ("Pano de Microfibra",      "Pano",     "Imporlens S.A."),
    ("Estuches Duros Normales", "Estuches", "Marilyn Imp."),
    ("Plaquetas Suaves",        "A3",       "Marilyn Imp."),
    ("Plaquetas Silicona",      "G19",      "Marilyn Imp."),
    ("Plaquetas Duras",         "A04",      "Marilyn Imp."),
]

print("Actualizando codigo_referencia y proveedor...")
errores = 0
for nombre, codigo, proveedor in ACTUALIZACIONES:
    try:
        supabase.table("inventario").update({
            "codigo_referencia": codigo,
            "proveedor": proveedor
        }).eq("nombre", nombre).execute()
        print(f"  OK: {codigo} - {nombre}")
    except Exception as e:
        print(f"  ERROR en {nombre}: {e}")
        errores += 1

print()
if errores == 0:
    print("Todos los productos actualizados con codigo y proveedor!")
else:
    print(f"Completado con {errores} errores.")
