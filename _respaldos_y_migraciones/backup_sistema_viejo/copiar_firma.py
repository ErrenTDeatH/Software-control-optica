"""Script temporal para copiar y procesar la firma"""
import shutil
from PIL import Image

src = r"C:\Users\Antho\.gemini\antigravity\brain\c017a6da-99c2-48d2-a7ee-301aa884cb2f\media__1776186585568.png"
dst = r"C:\Users\Antho\Happy app\firma.png"

img = Image.open(src).convert("RGBA")
# Pegar sobre fondo blanco para compatibilidad con FPDF
bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
bg.paste(img, (0, 0), img)
bg.convert("RGB").save(dst, format="PNG")
print(f"Firma guardada: {dst}, tamaño: {img.size}")
