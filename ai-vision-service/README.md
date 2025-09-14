# AI Service

Endpoints:
- GET /health
- GET /animals
- GET /animals/{id}
- GET /images/{filename}
- POST /classify (multipart image)
- POST /chat (OpenAI-backed)

Training:
- Dataset: `app/dog_breed/<ClassName>/*`
- Run: `python -m app.train` (inside container or venv)
- Outputs: `models/dog_breed_classifier.pth`, `models/class_map.json`

Env:
- OPENAI_API_KEY, OPENAI_MODEL (or Azure endpoints)
- MODEL_PTH_PATH, CLASS_MAP_PATH
