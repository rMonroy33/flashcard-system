# ⚡ FlashGen - Generador de Flashcards desde Documentos

Sistema web simple para subir documentos (PDF, DOCX, TXT) y generar flashcards automáticamente usando la API de MiniMax.

## Requisitos

- Python 3.8+
- API Key de MiniMax

## Instalación

```bash
cd flashcard-system
pip install --user --break-system-packages -r requirements.txt
```

## Configuración

Crear un archivo `.env` o exportar las variables:

```bash
export MINIMAX_API_KEY="tu_api_key_aqui"
```

Obtener API key en: https://platform.minimax.chat/

## Ejecutar

```bash
python3 server.py
```

El servidor arranca en: **http://localhost:8080**

## Acceso Remoto

El servidor corre en `0.0.0.0:8080`, accesible desde cualquier IP de la red.

Para acceder desde otro dispositivo:
```
http://IP_DEL_SERVIDOR:8080
```

## Uso

1. Abrir la web
2. Arrastrar o seleccionar un documento (PDF, DOCX, TXT)
3. Hacer click en "Generar Flashcards"
4. ¡Listo! Puedes ver las cards y estudiar

## API Endpoints

- `GET /` - Interfaz web
- `POST /upload` - Subir documento y generar flashcards
- `GET /api/decks` - Listar todos los mazos
- `GET /api/decks/{id}/export` - Exportar un deck en JSON
- `GET /deck/{id}` - Ver un deck específico

## Estructura

```
flashcard-system/
├── server.py        # Servidor FastAPI
├── requirements.txt # Dependencias
├── .env.example     # Ejemplo de configuración
└── flashcards_data/  # (creado automatico) albums de flashcards