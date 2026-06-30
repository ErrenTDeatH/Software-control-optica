-- ══════════════════════════════════════════════════════════════
-- HAPPY VISION · Migración: Columnas faltantes en historias_clinicas
-- Ejecutar en Supabase > SQL Editor
-- ══════════════════════════════════════════════════════════════

-- 1. Agregar columna optometrista (nombre del optometrista que atendió)
ALTER TABLE historias_clinicas 
ADD COLUMN IF NOT EXISTS optometrista TEXT DEFAULT '';

-- 2. Agregar columna optometrista_login (username del optometrista)
ALTER TABLE historias_clinicas 
ADD COLUMN IF NOT EXISTS optometrista_login TEXT DEFAULT '';

-- 3. Verificar que las columnas se crearon correctamente
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'historias_clinicas'
ORDER BY ordinal_position;
