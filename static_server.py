"""
StudyCards - Versión estática para GitHub Pages
Solo sirve archivos estáticos (HTML/CSS/JS)
"""

from pathlib import Path

# Los archivos estáticos están en la carpeta 'static'
# Esta versión es para subir a GitHub Pages o cualquier hosting estático

STATIC_DIR = Path(__file__).parent / "static"

# Archivos disponibles:
# - index.html (página principal)
# - sw.js (service worker para PWA)
# - manifest.json (config PWA)

print("=" * 50)
print("📚 StudyCards - Versión Estática")
print("=" * 50)
print()
print("Esta versión es para subir a GitHub Pages.")
print("Archivos en:", STATIC_DIR)
print()
print("Pasos para deploy:")
print("1. Ir a GitHub, crear repo nuevo")
print("2. Subir los archivos de la carpeta 'static'")
print("3. Settings → Pages → Source: main")
print("4. Esperar ~2 min y listo!")
print()
print("=" * 50)