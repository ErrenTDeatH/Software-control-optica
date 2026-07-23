from dotenv import load_dotenv
load_dotenv()
from supabase import create_client
import os

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

# Actualizar TODAS las historias con optometrista vacio
res = supabase.table('historias_clinicas').update({
    'optometrista': 'Opt. Anthonny Guato',
    'optometrista_login': 'admin'
}).eq('optometrista', '').execute()

print('Update ejecutado.')

# Verificar resultado
check = supabase.table('historias_clinicas').select('id, optometrista').execute()
exito = 0
for r in check.data:
    opto = r.get('optometrista', '')
    estado = 'OK' if opto else 'VACIO'
    print(f'  [{estado}] ID {r["id"]}: {opto}')
    if opto:
        exito += 1

print(f'\nTotal actualizados: {exito} / {len(check.data)}')
