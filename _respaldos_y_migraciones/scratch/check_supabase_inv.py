import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

res = supabase.table("inventario").select("count", count="exact").execute()
print(f"Productos en Supabase: {res.count}")

if res.count > 0:
    res = supabase.table("inventario").select("*").limit(5).execute()
    print("Primeros 5 productos:")
    for item in res.data:
        print(f" - {item.get('nombre')} ({item.get('marca')})")
