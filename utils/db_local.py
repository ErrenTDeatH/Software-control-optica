import sqlite3
import pandas as pd
import json
import os
from datetime import datetime

DB_PATH = "optica.db"

class LocalDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # Tabla: usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                nombre TEXT,
                sucursal TEXT,
                accesos TEXT,
                creado_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla: pacientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identificacion TEXT UNIQUE,
                nombre TEXT,
                nombres TEXT,
                apellidos TEXT,
                genero TEXT,
                direccion TEXT,
                edad TEXT,
                fecha_nacimiento TEXT,
                telefono TEXT,
                correo TEXT,
                ocupacion TEXT,
                sucursal TEXT,
                creado_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla: historias_clinicas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historias_clinicas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                paciente_nombre TEXT,
                fecha TEXT,
                ant_personales TEXT,
                ant_familiares TEXT,
                motivo TEXT,
                diabetes TEXT,
                hipertension TEXT,
                patologia_otra TEXT,
                observaciones TEXT,
                lenso_od TEXT,
                lenso_av_lej_od TEXT,
                lenso_av_cer_od TEXT,
                lenso_oi TEXT,
                lenso_av_lej_oi TEXT,
                lenso_av_cer_oi TEXT,
                rx_od TEXT,
                rx_av_lej_od TEXT,
                rx_av_cer_od TEXT,
                rx_oi TEXT,
                rx_av_lej_oi TEXT,
                rx_av_cer_oi TEXT,
                estado_muscular TEXT,
                seg_externo TEXT,
                test_colores TEXT,
                estado_refractivo TEXT,
                diagnostico TEXT,
                disposicion TEXT,
                recomendaciones TEXT,
                meses_proximo_control TEXT,
                necesita_lentes TEXT,
                test_color TEXT,
                sucursal TEXT,
                creado_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
            )
        """)

        # Tabla: historias_lc
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historias_lc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                paciente_nombre TEXT,
                fecha TEXT,
                sucursal TEXT,
                optometrista TEXT,
                optometrista_login TEXT,
                lc_usuario_previo TEXT,
                lc_tipo_lente_ant TEXT,
                lc_marca_ant TEXT,
                lc_horas_uso TEXT,
                lc_solucion_habitual TEXT,
                lc_motivo_consulta TEXT,
                lc_avsc_od TEXT,
                lc_avsc_oi TEXT,
                lc_rx_od TEXT,
                lc_rx_oi TEXT,
                lc_distancia_vertice TEXT,
                lc_kera_od TEXT,
                lc_kera_oi TEXT,
                lc_astig_corneal_od TEXT,
                lc_astig_corneal_oi TEXT,
                lc_parpados TEXT,
                lc_conjuntiva TEXT,
                lc_eversion TEXT,
                lc_cornea TEXT,
                lc_but_od TEXT,
                lc_but_oi TEXT,
                lc_menisco TEXT,
                lc_prueba_tipo TEXT,
                lc_prueba_od TEXT,
                lc_prueba_oi TEXT,
                lc_centrado TEXT,
                lc_movimiento TEXT,
                lc_pushup TEXT,
                lc_rotacion TEXT,
                lc_sobre_od TEXT,
                lc_sobre_oi TEXT,
                lc_final_od TEXT,
                lc_final_oi TEXT,
                lc_marca_final TEXT,
                lc_modalidad TEXT,
                lc_regimen TEXT,
                lc_solucion_final TEXT,
                lc_insercion TEXT,
                lc_fecha_entrega TEXT,
                lc_proximo_control TEXT,
                lc_observaciones TEXT,
                recomendaciones TEXT,
                creado_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
            )
        """)

        # Tabla: inventario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marca TEXT,
                modelo TEXT,
                color TEXT,
                cantidad_disponible INTEGER DEFAULT 0,
                precio_venta REAL DEFAULT 0,
                costo REAL DEFAULT 0,
                sucursal TEXT,
                creado_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla: ordenes_trabajo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordenes_trabajo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                paciente_nombre TEXT,
                creado_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado TEXT DEFAULT 'Pendiente',
                sucursal TEXT,
                prescripcion TEXT, -- JSON string
                detalle_lentes TEXT,
                tipo_lente_laboratorio TEXT,
                distancia_pupilar TEXT,
                valor_total REAL DEFAULT 0,
                abono REAL DEFAULT 0,
                saldo REAL DEFAULT 0,
                metodo_pago TEXT,
                usuario_creador TEXT,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
            )
        """)

        # Tabla: ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cliente TEXT,
                total REAL,
                costo_total REAL,
                metodo_pago TEXT,
                detalles TEXT, -- JSON string
                sucursal TEXT,
                usuario TEXT
            )
        """)

        # Tabla: gastos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                monto REAL,
                categoria TEXT,
                descripcion TEXT,
                usuario TEXT,
                sucursal TEXT
            )
        """)

        # Tabla: caja_diaria
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caja_diaria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                monto_apertura REAL,
                monto_cierre REAL,
                abierta_por TEXT,
                cerrada_por TEXT,
                sucursal TEXT,
                estado TEXT DEFAULT 'Abierta'
            )
        """)

        # Tabla: auditoria
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario TEXT,
                nombre_usuario TEXT,
                accion TEXT,
                entidad TEXT,
                detalle TEXT,
                sucursal TEXT
            )
        """)

        # Tabla: sucursales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sucursales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                direccion TEXT,
                telefono TEXT,
                ciudad TEXT
            )
        """)

        # Insertar sucursal por defecto si no existe
        cursor.execute("INSERT OR IGNORE INTO sucursales (nombre) VALUES ('Matriz')")
        
        # Insertar admin por defecto si no hay usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            # Pass por defecto: admin123 (en texto plano por ahora, como estaba en el esquema anterior)
            cursor.execute("""
                INSERT INTO usuarios (username, password, role, nombre, sucursal, accesos) 
                VALUES ('admin', 'admin123', 'Administrador', 'Administrador Sistema', 'Matriz', ?)
            """, (json.dumps(["Inicio", "Pacientes", "Generar Orden", "Trabajos", "Ventas", "Inventario", "Contabilidad", "Usuarios", "Configuracion"]),))

        self.conn.commit()

    def query(self, sql, params=()):
        return pd.read_sql_query(sql, self.conn, params=params)

    def execute(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        return cursor.lastrowid

    def get_all(self, table):
        return pd.read_sql_query(f"SELECT * FROM {table}", self.conn)

local_db = LocalDB()
