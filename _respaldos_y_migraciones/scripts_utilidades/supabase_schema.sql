-- Script para crear las tablas en Supabase (VERSION 3 - CON POLITICAS ABIERTAS)
-- Pega esto en el "SQL Editor" de Supabase y dale a "Run"

-- 1. Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT,
    nombre TEXT,
    cargo TEXT,
    registro TEXT,
    telefono TEXT,
    firma_base64 TEXT
);
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all" ON usuarios;
CREATE POLICY "Allow all" ON usuarios FOR ALL TO anon USING (true) WITH CHECK (true);

-- 2. Tabla de Pacientes
CREATE TABLE IF NOT EXISTS pacientes (
    id TEXT PRIMARY KEY,
    identificacion TEXT,
    nombre TEXT,
    nombres TEXT,
    apellidos TEXT,
    genero TEXT,
    direccion TEXT,
    edad TEXT,
    fecha_nacimiento TEXT,
    telefono TEXT,
    correo TEXT,
    ocupacion TEXT
);
ALTER TABLE pacientes ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all" ON pacientes;
CREATE POLICY "Allow all" ON pacientes FOR ALL TO anon USING (true) WITH CHECK (true);

-- 3. Tabla de Historias Clínicas
CREATE TABLE IF NOT EXISTS historias_clinicas (
    id TEXT PRIMARY KEY,
    paciente_id TEXT,
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
    test_color TEXT
);
ALTER TABLE historias_clinicas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all" ON historias_clinicas;
CREATE POLICY "Allow all" ON historias_clinicas FOR ALL TO anon USING (true) WITH CHECK (true);

-- 4. Tabla de Citas
CREATE TABLE IF NOT EXISTS citas (
    id BIGSERIAL PRIMARY KEY,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    paciente_nombre TEXT NOT NULL,
    telefono TEXT,
    motivo TEXT,
    optometrista TEXT,
    sucursal TEXT NOT NULL,
    estado TEXT DEFAULT 'Pendiente'
);
ALTER TABLE citas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all" ON citas;
CREATE POLICY "Allow all" ON citas FOR ALL TO anon USING (true) WITH CHECK (true);

-- 5. Tabla de Ventas
CREATE TABLE IF NOT EXISTS ventas (
    id BIGSERIAL PRIMARY KEY,
    cliente TEXT NOT NULL,
    identificacion TEXT,
    total DOUBLE PRECISION NOT NULL,
    costo_total DOUBLE PRECISION,
    abono DOUBLE PRECISION,
    saldo DOUBLE PRECISION,
    metodo_pago TEXT,
    sucursal TEXT,
    detalles JSONB,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
ALTER TABLE ventas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all" ON ventas;
CREATE POLICY "Allow all" ON ventas FOR ALL TO anon USING (true) WITH CHECK (true);
