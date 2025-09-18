# AI Service

Endpoints:
- GET /health
- GET /animals
- GET /animals/{id}
- GET /images/{filename}
- POST /classify (multipart image)

Through Nginx (default config):
- /ai/* → ai-vision (this service)
- /ai/chat → ai-chatbot service

Training:
- Dataset: `app/dog_breed/<ClassName>/*`
- Run: `python -m app.train` (inside container or venv)
- Outputs: `models/dog_breed_classifier.pth`, `models/class_map.json`

Env:
- OPENAI_API_KEY, OPENAI_MODEL (or Azure endpoints)
- MODEL_PTH_PATH, CLASS_MAP_PATH

## CPU/GPU build & run

- CPU (default, works everywhere including macOS/Apple Silicon):
	- Uses `python:3.11-slim` base and CPU-only PyTorch wheels.
	- Build and start via root compose:
		- `docker compose build ai-vision`
		- `docker compose up -d ai-vision`

- GPU (Linux/WSL2 with NVIDIA):
	- Uses `nvidia/cuda:12.1.1-cudnn8-runtime` and CUDA wheels.
	- Requires NVIDIA driver and `nvidia-container-toolkit`.
	- Build and start with overlay:
		- `docker compose -f docker-compose.yml -f docker-compose.gpu.yml build ai-vision`
		- `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d ai-vision`

Notes:
- macOS Docker cannot access GPU; it will run CPU automatically. For local native macOS (non-Docker) you may leverage PyTorch MPS.
- Large datasets/models are excluded from the image and mounted as volumes.
- To (re)train inside the container, set `TRAIN_ON_START=1` and provide dataset under `app/dog_breed/` (mounted at build or via volume).

## Image slimming choices
- CPU image: slim base + headless runtime libs only (`libgl1`, `libglib2.0-0`).
- PyTorch CPU wheels (no CUDA) for minimal size.
- `.dockerignore` excludes datasets, models, indices, and caches.

## CPU vs GPU

Default image is CPU-only and slim. To run GPU on Linux/WSL2 with NVIDIA GPUs:

1) Install NVIDIA driver and nvidia-container-toolkit
2) Build and run with the GPU overlay:

```
docker compose -f ../docker-compose.yml -f ../docker-compose.gpu.yml build ai-vision
docker compose -f ../docker-compose.yml -f ../docker-compose.gpu.yml up -d ai-vision
```

On macOS (Intel/Apple Silicon), Docker cannot access the host GPU; the service will run on CPU automatically.
