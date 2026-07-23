import os
import json
import sqlite3
import base64
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: No se encontraron las credenciales de Supabase en el archivo .env")
    exit(1)

# Inicializar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def clean_df(df):
    """Reemplaza NaN y valores no compatibles con JSON por None/string vacio."""
    # Convertir todo a string primero para evitar problemas de tipos mixtos
    df = df.astype(str)
    # Reemplazar representaciones de nulos por None (que se convierte a null en JSON)
    df = df.replace(["nan", "NaN", "None", "None", "NULL", "null"], None)
    return df

def migrar_usuarios():
    print("Migrando usuarios...")
    try:
        if os.path.exists("usuarios.json"):
            with open("usuarios.json", "r", encoding="utf-8") as f:
                usuarios = json.load(f)
            
            for username, data in usuarios.items():
                firma_b64 = None
                firma_path = f"firma_{username}.png"
                if os.path.exists(firma_path):
                    try:
                        with open(firma_path, "rb") as f_img:
                            firma_b64 = base64.b64encode(f_img.read()).decode()
                    except Exception as e:
                        print(f"  Error al leer firma de {username}: {e}")
                
                user_data = {
                    "username": str(username),
                    "password": str(data.get("password", "")),
                    "role": str(data.get("role", "Optometrista")),
                    "nombre": str(data.get("nombre", username)),
                    "cargo": str(data.get("cargo", "Optometrista")),
                    "registro": str(data.get("registro", "")),
                    "telefono": str(data.get("telefono", "")),
                    "firma_base64": firma_b64
                }
                
                supabase.table("usuarios").upsert(user_data).execute()
                print(f"  Usuario '{username}' migrado.")
        else:
            print("  No se encontro usuarios.json.")
    except Exception as e:
        print(f"Error al migrar usuarios: {e}")

def migrar_pacientes():
    print("Migrando pacientes...")
    try:
        conn = sqlite3.connect("happy_vision.db")
        df = pd.read_sql_query("SELECT * FROM pacientes", conn)
        conn.close()
        
        if len(df) == 0:
            print("  No hay pacientes para migrar.")
            return

        # Filtrar solo las columnas que sabemos que estan en Supabase
        cols_ok = [
            "id", "identificacion", "nombre", "nombres", "apellidos",
            "genero", "direccion", "edad", "fecha_nacimiento",
            "telefono", "correo", "ocupacion"
        ]
        # Si el DF tiene mas columnas (como creado_en), las ignoramos para evitar errores de schema
        df_filtered = df[[c for c in cols_ok if c in df.columns]]
        
        df_filtered = clean_df(df_filtered)
        records = df_filtered.to_dict(orient="records")
        
        batch_size = 100
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            supabase.table("pacientes").upsert(batch).execute()
            print(f"  Pacientes {i} a {i+len(batch)} migrados.")
            
    except Exception as e:
        print(f"Error al migrar pacientes: {e}")

def migrar_historias():
    print("Migrando historias clinicas...")
    try:
        conn = sqlite3.connect("happy_vision.db")
        df = pd.read_sql_query("SELECT * FROM historias_clinicas", conn)
        conn.close()
        
        if len(df) == 0:
            print("  No hay historias clinicas para migrar.")
            return

        cols_ok = [
            "id", "paciente_id", "paciente_nombre", "fecha",
            "ant_personales", "ant_familiares", "motivo",
            "diabetes", "hipertension", "patologia_otra", "observaciones",
            "lenso_od", "lenso_av_lej_od", "lenso_av_cer_od",
            "lenso_oi", "lenso_av_lej_oi", "lenso_av_cer_oi",
            "rx_od", "rx_av_lej_od", "rx_av_cer_od",
            "rx_oi", "rx_av_lej_oi", "rx_av_cer_oi",
            "estado_muscular", "seg_externo", "test_colores", "estado_refractivo",
            "diagnostico", "disposicion", "recomendaciones",
            "meses_proximo_control", "necesita_lentes", "test_color"
        ]
        df_filtered = df[[c for c in cols_ok if c in df.columns]]
        
        df_filtered = clean_df(df_filtered)
        records = df_filtered.to_dict(orient="records")
        
        batch_size = 50
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            supabase.table("historias_clinicas").upsert(batch).execute()
            print(f"  Historias {i} a {i+len(batch)} migradas.")
            
    except Exception as e:
        print(f"Error al migrar historias clinicas: {e}")

if __name__ == "__main__":
    print("=== INICIANDO MIGRACION A SUPABASE (FIXED) ===")
    migrar_usuarios()
    migrar_pacientes()
    migrar_historias()
    print("=== MIGRACION FINALIZADA ===")
