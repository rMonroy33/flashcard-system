# 📚 StudyCards - Sistema de Flashcards

Dos versiones en un solo repo:

## 🌐 Versión Estática (GitHub Pages)

Para subir a GitHub Pages y acceder desde cualquier lugar.

**Archivos:** `static/` (index.html, sw.js, manifest.json)

**Deploy:**
1. Subir carpeta `static/` a GitHub
2. Settings → Pages → Source: main
3. Esperar ~2 min

**Instalar como app:**
- iOS: Safari → Compartir → Añadir a pantalla de inicio
- Android: Chrome → Menú → Instalar app

⚠️ **Limitación:** Sin backend, las tarjetas se crean a mano y se guardan en localStorage.

---

## ⚡ Versión Completa con IA (Local)

Tiene procesamiento automático de documentos (PDF, DOCX, TXT) usando la API de MiniMax para generar flashcards.

### Archivos

```
flashcard-system/
├── server.py          # Servidor FastAPI (este corrés)
├── requirements.txt  # Dependencias
├── .env.example      # Configuración de ejemplo
└── flashcards_data/  # (creado automático) albums de flashcards
```

### Instalación

```bash
# 1. Instalar dependencias
pip install --user --break-system-packages -r requirements.txt

# 2. Configurar API key de MiniMax
cp .env.example .env
# Editar .env y poner tu MINIMAX_API_KEY

# 3. Arrancar
python3 server.py
```

### Uso

1. Abrir http://localhost:8080
2. Subir un PDF, DOCX o TXT
3. El sistema genera flashcards automáticamente
4. Estudiar desde la web

### Acceso remoto (para otra persona)

**Opción A: ngrok (temporal)**
```bash
ngrok http 8080
# Te da una URL para compartir
```

**Opción B: Deploy a Railway (permanente)**
```bash
# Crear repo en GitHub
# Conectar a Railway (railway.app)
# Deploy automático
# URL fija para compartir
```

### API Endpoints

- `GET /` - Interfaz web
- `POST /upload` - Subir documento y generar flashcards
- `GET /api/decks` - Listar todos los mazos
- `GET /api/decks/{id}/export` - Exportar deck en JSON
- `GET /deck/{id}` - Ver deck específico

---

## 📱 PWA

Ambas versiones soportan PWA:
- Funcionan offline
- Se instalan en el celular como app native
- Datos guardados localmente

---

## 🔒 Privacidad

- Versión estática: datos solo en localStorage del navegador
- Versión IA: datos en el servidor local, API key necesaria