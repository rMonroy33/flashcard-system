# 📚 StudyCards - Gestor de Tareas de Estudio

Sistema simple de tarjetas de estudio (flashcards) en HTML + CSS + JS puro. Funciona como **PWA** (se instala en el celular como app) y los datos se guardan en **localStorage** del navegador.

## ✨ Características

- ✅ Agregar, editar y eliminar tarjetas
- ✅ Marcar como completadas
- ✅ Filtrar por estado (pendientes/completadas/materia)
- ✅ Estadísticas (total, pendientes, completadas)
- ✅ PWA - Se instala en el celular como app native
- ✅ Funciona offline
- ✅ Datos guardados en el navegador (localStorage)
- ✅ Responsive - funciona en celular y desktop

## 📱 Instalación en iOS/Android

1. Abrir en Safari (iOS) o Chrome (Android)
2. Ir a la URL de GitHub Pages
3. **iOS:** Compartir → Añadir a pantalla de inicio
4. **Android:** Menú → Instalar app

## 🚀 Deploy a GitHub Pages

1. Crear repositorio nuevo en GitHub
2. Subir los archivos de la carpeta `static/`:
   - `index.html`
   - `sw.js`
   - `manifest.json`
3. Ir a **Settings → Pages**
4. En "Source" seleccionar `main` y guardar
5. Esperar ~2 minutos
6. ¡Listo! Tu app estará en: `https://tu-usuario.github.io/repo-name/`

## 🛠️ Desarrollo local

Simplemente abrir `static/index.html` en el navegador.

O usar un servidor local:
```bash
cd flashcard-system
python3 -m http.server 8080
# Abrir http://localhost:8080/static/index.html
```

## 📁 Estructura

```
flashcard-system/
├── server.py          # Servidor con procesamiento AI (versión completa)
├── static/            # Archivos para GitHub Pages (esta versión simple)
│   ├── index.html     # App principal
│   ├── sw.js          # Service Worker (PWA)
│   └── manifest.json   # Config PWA
└── README.md          # Este archivo
```

## ⚙️ Configuración

No necesita ninguna configuración. Todo se guarda en localStorage del navegador.

Si querés cambiar materias, editá el `<select id="subjectInput">` en el HTML.

## 🔒 Privacidad

Los datos **nunca** salen de tu navegador. Todo se almacena en localStorage. Ni yo ni GitHub tienen acceso a tus tareas.

---

¿Querés la versión completa con IA? Volvé a la versión `server.py` que usa MiniMax para generar flashcards automáticamente desde documentos PDF/DOCX.