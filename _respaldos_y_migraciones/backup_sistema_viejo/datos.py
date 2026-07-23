"""
utils/datos.py — Generación de datos de prueba para Happy Vision
"""

import pandas as pd
import random
from datetime import datetime, timedelta


def generate_sample_data():
    """Genera datos de prueba realistas para Happy Vision."""
    pacientes = [
        "Maria Garcia", "Carlos Lopez", "Ana Martinez", "Jose Rodriguez",
        "Laura Perez", "Luis Hernandez", "Carmen Torres", "Miguel Flores",
        "Sandra Ramirez", "Diego Morales", "Patricia Jimenez", "Roberto Castro",
        "Daniela Vega", "Andres Reyes", "Valentina Cruz", "Felipe Nunez",
        "Camila Herrera", "Sebastian Ruiz", "Natalia Mendoza", "Alejandro Diaz",
    ]
    tipos_lente  = ["Monofocal", "Progresivo", "Progresivo Premium", "Filtro Azul", "Contactologia"]
    laboratorios = ["Indulentes", "Pecsa/ImportVision", "Stock propio"]
    metodos_pago = ["Efectivo", "Tarjeta Debito", "Tarjeta Credito", "Transferencia"]

    precios = {
        "Monofocal":          (80,  160),
        "Progresivo":         (180, 290),
        "Progresivo Premium": (290, 520),
        "Filtro Azul":        (120, 210),
        "Contactologia":      (55,  130),
    }

    random.seed(42)
    trabajos = []
    today = datetime.today()

    for i in range(60):
        days_ago = random.randint(0, 89)
        fecha    = today - timedelta(days=days_ago)
        paciente = random.choice(pacientes)
        tipo     = random.choice(tipos_lente)
        lab      = random.choice(laboratorios)
        metodo   = random.choice(metodos_pago)
        p_min, p_max = precios[tipo]
        precio   = round(random.uniform(p_min, p_max), 2)
        pct_abono = random.choice([0.3, 0.5, 0.7, 1.0, 1.0])
        abono    = round(min(precio * pct_abono, precio), 2)
        saldo    = round(precio - abono, 2)

        trabajos.append({
            "id":              i + 1,
            "fecha":           fecha.strftime("%Y-%m-%d"),
            "paciente":        paciente,
            "tipo_lente":      tipo,
            "laboratorio":     lab,
            "precio_total":    precio,
            "abono":           abono,
            "metodo_pago":     metodo,
            "saldo_pendiente": saldo,
            "estado":          "Pagado" if saldo < 1 else ("Parcial" if abono > 0 else "Pendiente"),
        })

    # ─── Inventario ───────────────────────────────────────────
    inventario = [
        {"id":1,  "categoria":"Armazones",  "subcategoria":"TR90",     "producto":"Armazon TR90 Negro",                   "stock":8,  "stock_min":5,  "unidad":"unid",   "costo":15.0, "precio":35.0},
        {"id":2,  "categoria":"Armazones",  "subcategoria":"TR90",     "producto":"Armazon TR90 Azul",                    "stock":3,  "stock_min":5,  "unidad":"unid",   "costo":15.0, "precio":35.0},
        {"id":3,  "categoria":"Armazones",  "subcategoria":"TR90",     "producto":"Armazon TR90 Rojo",                    "stock":6,  "stock_min":4,  "unidad":"unid",   "costo":14.0, "precio":32.0},
        {"id":4,  "categoria":"Armazones",  "subcategoria":"TR90",     "producto":"Armazon TR90 Gris",                    "stock":2,  "stock_min":5,  "unidad":"unid",   "costo":15.0, "precio":35.0},
        {"id":5,  "categoria":"Armazones",  "subcategoria":"Acetato",  "producto":"Armazon Acetato Havana",               "stock":10, "stock_min":4,  "unidad":"unid",   "costo":20.0, "precio":55.0},
        {"id":6,  "categoria":"Armazones",  "subcategoria":"Acetato",  "producto":"Armazon Acetato Negro Mate",           "stock":7,  "stock_min":4,  "unidad":"unid",   "costo":18.0, "precio":48.0},
        {"id":7,  "categoria":"Armazones",  "subcategoria":"Acetato",  "producto":"Armazon Acetato Carey",                "stock":1,  "stock_min":3,  "unidad":"unid",   "costo":22.0, "precio":60.0},
        {"id":8,  "categoria":"Armazones",  "subcategoria":"Acetato",  "producto":"Armazon Acetato Transparente",         "stock":5,  "stock_min":3,  "unidad":"unid",   "costo":21.0, "precio":55.0},
        {"id":9,  "categoria":"Plaquetas",  "subcategoria":"Suaves",   "producto":"Plaqueta suave transparente (par)",    "stock":25, "stock_min":10, "unidad":"par",    "costo":0.50, "precio":2.0},
        {"id":10, "categoria":"Plaquetas",  "subcategoria":"Suaves",   "producto":"Plaqueta suave blanca (par)",          "stock":8,  "stock_min":10, "unidad":"par",    "costo":0.50, "precio":2.0},
        {"id":11, "categoria":"Plaquetas",  "subcategoria":"Suaves",   "producto":"Plaqueta suave nose pad (par)",        "stock":14, "stock_min":8,  "unidad":"par",    "costo":0.60, "precio":2.5},
        {"id":12, "categoria":"Plaquetas",  "subcategoria":"Silicona", "producto":"Plaqueta silicona anti-alergica (par)","stock":30, "stock_min":10, "unidad":"par",    "costo":0.80, "precio":3.5},
        {"id":13, "categoria":"Plaquetas",  "subcategoria":"Silicona", "producto":"Plaqueta silicona con tornillo (par)", "stock":4,  "stock_min":8,  "unidad":"par",    "costo":1.00, "precio":4.0},
        {"id":14, "categoria":"Plaquetas",  "subcategoria":"Silicona", "producto":"Plaqueta silicona oval larga (par)",   "stock":6,  "stock_min":8,  "unidad":"par",    "costo":0.90, "precio":3.5},
        {"id":15, "categoria":"Liquidos",   "subcategoria":"Limpieza", "producto":"Spray limpiador lentes 120ml",         "stock":12, "stock_min":6,  "unidad":"frasco", "costo":3.50, "precio":8.0},
        {"id":16, "categoria":"Liquidos",   "subcategoria":"Limpieza", "producto":"Spray limpiador lentes 250ml",         "stock":2,  "stock_min":4,  "unidad":"frasco", "costo":5.50, "precio":12.0},
        {"id":17, "categoria":"Liquidos",   "subcategoria":"Limpieza", "producto":"Solucion limpiadora ultrasonica 500ml","stock":5,  "stock_min":3,  "unidad":"frasco", "costo":8.00, "precio":18.0},
        {"id":18, "categoria":"Liquidos",   "subcategoria":"Limpieza", "producto":"Pano microfibra premium",              "stock":3,  "stock_min":15, "unidad":"unid",   "costo":0.80, "precio":3.0},
        {"id":19, "categoria":"Liquidos",   "subcategoria":"Limpieza", "producto":"Toallitas humedas lentes (caja 100)",  "stock":4,  "stock_min":3,  "unidad":"caja",   "costo":4.00, "precio":9.0},
    ]

    # ─── Gastos Operativos ────────────────────────────────────
    random.seed(7)
    gastos = []
    conceptos = [
        ("Arriendo local",        "Fijo",     800),
        ("Servicios basicos",     "Fijo",     120),
        ("Internet y telefono",   "Fijo",      45),
        ("Salario asistente",     "Fijo",     600),
        ("Publicidad redes",      "Variable",  80),
        ("Materiales de oficina", "Variable",  30),
        ("Transporte y envios",   "Variable",  40),
        ("Mantenimiento equipos", "Variable",   0),
    ]
    for month_offset in range(3):
        month_date = today - timedelta(days=30 * month_offset)
        mes_str = month_date.strftime("%Y-%m")
        for concepto, tipo, monto_base in conceptos:
            if monto_base > 0:
                variacion = random.uniform(0.93, 1.07)
                gastos.append({
                    "fecha":    mes_str,
                    "concepto": concepto,
                    "tipo":     tipo,
                    "monto":    round(monto_base * variacion, 2),
                })
        if random.random() > 0.4:
            gastos.append({
                "fecha":    mes_str,
                "concepto": "Mantenimiento equipos",
                "tipo":     "Variable",
                "monto":    round(random.uniform(50, 220), 2),
            })

    # ─── DataFrames vacíos para Pacientes/Historias (se llenan desde SQLite) ─
    df_p = pd.DataFrame(columns=[
        "id", "identificacion", "nombre", "nombres", "apellidos",
        "genero", "direccion", "edad", "fecha_nacimiento",
        "telefono", "correo", "ocupacion"
    ])
    df_h = pd.DataFrame(columns=[
        "id", "paciente_id", "paciente_nombre", "fecha",
        "ant_personales", "ant_familiares", "motivo",
        "diabetes", "hipertension", "patologia_otra", "observaciones",
        "lenso_od", "lenso_av_lej_od", "lenso_av_cer_od",
        "lenso_oi", "lenso_av_lej_oi", "lenso_av_cer_oi",
        "rx_od", "rx_av_lej_od", "rx_av_cer_od",
        "rx_oi", "rx_av_lej_oi", "rx_av_cer_oi",
        "estado_muscular", "seg_externo", "test_colores",
        "estado_refractivo", "diagnostico", "disposicion", "recomendaciones",
        "meses_proximo_control",
    ])

    return (
        pd.DataFrame(trabajos),
        pd.DataFrame(inventario),
        pd.DataFrame(gastos),
        df_p,
        df_h,
    )
