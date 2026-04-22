"""
FlashGen - Sistema de generación de flashcards desde documentos
Usando FastAPI + MiniMax API
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# ============== CONFIGURACIÓN ==============
STORAGE_DIR = Path("flashcards_data")
STORAGE_DIR.mkdir(exist_ok=True)

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_MODEL = "MiniMax-Text-01"  # MiniMax M2.7 para texto

# ============== MODELOS ==============
class Flashcard(BaseModel):
    id: str
    question: str
    answer: str
    source_doc: str
    created_at: str

class DeckCreate(BaseModel):
    name: str
    description: Optional[str] = ""

# ============== HELPERS ==============
def extract_text_from_file(filepath: Path) -> str:
    """Extrae texto de PDF, DOCX o TXT"""
    ext = filepath.suffix.lower()
    
    if ext == ".pdf":
        try:
            import PyPDF2
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error leyendo PDF: {e}")
    
    elif ext in [".docx", ".doc"]:
        try:
            from docx import Document
            doc = Document(filepath)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error leyendo DOCX: {e}")
    
    elif ext == ".txt":
        return filepath.read_text(encoding="utf-8", errors="ignore")
    
    else:
        raise HTTPException(status_code=400, detail=f"Formato no soportado: {ext}")

def generate_flashcards_with_minimax(text: str, doc_name: str) -> List[dict]:
    """Genera flashcards usando MiniMax API"""
    if not MINIMAX_API_KEY:
        raise HTTPException(status_code=500, detail="MINIMAX_API_KEY no configurada")
    
    # Preparar el texto para enviar (máximo ~8000 caracteres para dejar espacio para el prompt)
    max_chars = 7000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... documento truncado ...]"
    
    prompt = f"""Eres un profesor experto. Analiza el siguiente texto y genera flashcards educativas.

Reglas:
- Genera entre 5 y 15 flashcards
- Cada flashcard debe tener una PREGUNTA y una RESPUESTA
- Las preguntas deben ser claras y específicas
- Las respuestas deben ser concisas (máximo 2-3 oraciones)
- Distribuye los temas del documento uniformemente
- Devuelve SOLO un JSON array con este formato exacto (sin texto adicional):

[
  {{"pregunta": "...", "respuesta": "..."}},
  {{"pregunta": "...", "respuesta": "..."}}
]

Texto del documento:
{text}

JSON:"""

    import urllib.request
    import urllib.error
    
    url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    
    payload = {
        "model": MINIMAX_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]
            
            # Limpiar el JSON de posibles markdown
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            flashcards_data = json.loads(content.strip())
            
            # Convertir a formato nuestro
            cards = []
            for card in flashcards_data:
                cards.append({
                    "id": str(uuid.uuid4())[:8],
                    "question": card.get("pregunta", card.get("question", "")),
                    "answer": card.get("respuesta", card.get("answer", "")),
                    "source_doc": doc_name,
                    "created_at": datetime.now().isoformat()
                })
            
            return cards
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise HTTPException(status_code=500, detail=f"Error de MiniMax API: {e.code} - {error_body}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando flashcards: {str(e)}")

def load_deck(deck_id: str) -> dict:
    """Carga un deck desde archivo"""
    deck_file = STORAGE_DIR / f"{deck_id}.json"
    if not deck_file.exists():
        raise HTTPException(status_code=404, detail="Deck no encontrado")
    return json.loads(deck_file.read_text())

def save_deck(deck_id: str, data: dict):
    """Guarda un deck a archivo"""
    deck_file = STORAGE_DIR / f"{deck_id}.json"
    deck_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))

# ============== FASTAPI APP ==============
app = FastAPI(title="FlashGen API", description="Sistema de generación de flashcards desde documentos")

# Endpoint: Página principal
@app.get("/", response_class=HTMLResponse)
async def home():
    return """<!DOCTYPE html>
<html>
<head>
    <title>FlashGen - Generador de Flashcards</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; }
        .container { max-width: 800px; margin: 0 auto; padding: 2rem; }
        h1 { text-align: center; color: #00d9ff; margin-bottom: 2rem; }
        .card { background: #16213e; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }
        .upload-zone { border: 2px dashed #00d9ff55; border-radius: 12px; padding: 2rem; text-align: center; cursor: pointer; transition: all 0.3s; }
        .upload-zone:hover { border-color: #00d9ff; background: #1a2744; }
        input[type="file"] { display: none; }
        .btn { background: #00d9ff; color: #1a1a2e; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 1rem; }
        .btn:hover { background: #00b8d9; }
        .deck-list { margin-top: 2rem; }
        .deck-item { display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: #16213e; border-radius: 8px; margin-bottom: 0.5rem; }
        .deck-item a { color: #00d9ff; text-decoration: none; }
        .deck-item a:hover { text-decoration: underline; }
        .flashcard { background: #16213e; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; }
        .flashcard .question { font-size: 1.1rem; color: #00d9ff; margin-bottom: 1rem; }
        .flashcard .answer { background: #0f3460; padding: 1rem; border-radius: 8px; color: #ccc; }
        .back { color: #00d9ff; text-decoration: none; display: inline-block; margin-bottom: 1rem; }
        .status { color: #aaa; font-size: 0.9rem; margin-top: 0.5rem; }
        .file-name { color: #00d9ff; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ FlashGen</h1>
        <p style="text-align:center; color:#888; margin-bottom:2rem;">Subí un documento (PDF, DOCX, TXT) y generá flashcards automáticamente</p>
        
        <div class="card">
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-zone" onclick="document.getElementById('fileInput').click()">
                    <p id="dropText">📄 Arrastrá un archivo o hacé click para seleccionar</p>
                    <p style="color:#666; font-size:0.85rem; margin-top:0.5rem;">PDF, DOCX, TXT (máx 10MB)</p>
                </div>
                <input type="file" id="fileInput" name="file" accept=".pdf,.docx,.doc,.txt" required>
                <div style="margin-top:1rem;">
                    <button type="submit" class="btn">✨ Generar Flashcards</button>
                </div>
            </form>
            <div id="status" class="status"></div>
        </div>
        
        <div class="deck-list">
            <h2 style="color:#00d9ff; margin-bottom:1rem;">Tus Mazos</h2>
            <div id="deckList">Cargando...</div>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('uploadForm');
        const status = document.getElementById('status');
        const deckList = document.getElementById('deckList');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) return;
            
            status.textContent = '⏳ Procesando documento...';
            status.style.color = '#ffaa00';
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/upload', { method: 'POST', body: formData });
                const result = await response.json();
                
                if (response.ok) {
                    status.textContent = '✅ ¡Flashcards generadas! Redirigiendo...';
                    status.style.color = '#00ff88';
                    setTimeout(() => window.location.href = '/deck/' + result.deck_id, 1000);
                } else {
                    status.textContent = '❌ Error: ' + result.detail;
                    status.style.color = '#ff4444';
                }
            } catch (err) {
                status.textContent = '❌ Error de conexión';
                status.style.color = '#ff4444';
            }
        });
        
        // Cargar lista de decks
        fetch('/api/decks').then(r => r.json()).then(data => {
            if (data.decks.length === 0) {
                deckList.innerHTML = '<p style="color:#666;">No hay mazos todavía</p>';
            } else {
                deckList.innerHTML = data.decks.map(d => `
                    <div class="deck-item">
                        <div>
                            <a href="/deck/${d.id}">${d.name}</a>
                            <div style="color:#666; font-size:0.85rem;">${d.card_count} cards • ${d.source}</div>
                        </div>
                        <a href="/api/decks/${d.id}/export" style="color:#888;">📥</a>
                    </div>
                `).join('');
            }
        });
    </script>
</body>
</html>"""

# Endpoint: Ver deck con flashcards
@app.get("/deck/{deck_id}", response_class=HTMLResponse)
async def view_deck(deck_id: str):
    try:
        deck = load_deck(deck_id)
    except Exception:
        return HTMLResponse("<h1>Deck no encontrado</h1><a href='/'>Volver</a>", status_code=404)
    
    cards_html = ""
    for card in deck["cards"]:
        cards_html += f"""
        <div class="flashcard">
            <div class="question" onclick="this.nextElementSibling.classList.toggle('hidden')">❓ {card['question']}</div>
            <div class="answer hidden" style="display:none;">✅ {card['answer']}</div>
        </div>"""
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{deck['name']} - FlashGen</title>
    <meta charset="utf-8">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; padding: 1rem; }}
        .container {{ max-width: 700px; margin: 0 auto; }}
        h1 {{ color: #00d9ff; margin-bottom: 0.5rem; }}
        .meta {{ color: #888; margin-bottom: 2rem; }}
        .flashcard {{ background: #16213e; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; cursor: pointer; }}
        .question {{ font-size: 1.1rem; color: #00d9ff; }}
        .answer {{ background: #0f3460; padding: 1rem; border-radius: 8px; margin-top: 1rem; color: #ccc; }}
        .hidden {{ display: none !important; }}
        .back {{ color: #00d9ff; text-decoration: none; display: inline-block; margin-bottom: 1rem; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back">← Volver</a>
        <h1>{deck['name']}</h1>
        <p class="meta">{len(deck['cards'])} flashcards • {deck['source']}</p>
        {cards_html}
    </div>
</body>
</html>"""

# Endpoint: Subir documento y generar
@app.post("/upload")
async def upload_and_generate(file: UploadFile = File(...)):
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Archivo muy grande (máx 10MB)")
    
    # Guardar archivo temporalmente
    temp_path = STORAGE_DIR / f"temp_{uuid.uuid4()}{Path(file.filename).suffix}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Extraer texto
        text = extract_text_from_file(temp_path)
        
        if len(text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Documento muy corto o sin texto legible")
        
        # Generar flashcards
        cards = generate_flashcards_with_minimax(text, file.filename)
        
        # Crear deck
        deck_id = str(uuid.uuid4())[:8]
        deck_data = {
            "id": deck_id,
            "name": file.filename.rsplit(".", 1)[0],
            "source": file.filename,
            "created_at": datetime.now().isoformat(),
            "cards": cards
        }
        
        save_deck(deck_id, deck_data)
        
        return JSONResponse({"deck_id": deck_id, "card_count": len(cards)})
    
    finally:
        # Limpiar archivo temporal
        temp_path.unlink(missing_ok=True)

# API: Listar decks
@app.get("/api/decks")
async def list_decks():
    decks = []
    for f in STORAGE_DIR.glob("*.json"):
        data = json.loads(f.read_text())
        decks.append({
            "id": data["id"],
            "name": data["name"],
            "source": data["source"],
            "card_count": len(data["cards"]),
            "created_at": data["created_at"]
        })
    return {"decks": sorted(decks, key=lambda x: x["created_at"], reverse=True)}

# API: Exportar deck
@app.get("/api/decks/{deck_id}/export")
async def export_deck(deck_id: str):
    deck = load_deck(deck_id)
    return JSONResponse(deck)

if __name__ == "__main__":
    print("=" * 50)
    print("⚡ FlashGen - Servidor de Flashcards")
    print("=" * 50)
    print()
    print("📍 Endpoints:")
    print("   🌐 http://localhost:8080        - Interfaz web")
    print("   📚 http://localhost:8080/docs  - Documentación API")
    print()
    print("⚙️  Configuración:")
    print(f"   MINIMAX_API_KEY: {'✓ Configurada' if MINIMAX_API_KEY else '✗ No configurada'}")
    print(f"   Almacenamiento: {STORAGE_DIR.absolute()}")
    print()
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8080)