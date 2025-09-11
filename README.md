# Hackathon Template (Spring Boot + FastAPI + Nginx + Bootstrap + Docker Compose)

## Quickstart (Local)
```bash
cp .env.example .env           # fill values (AI_MODE=fake first)
docker compose build
docker compose up -d
# Open: http://localhost/
```

### Switch to real mode (.pth + OpenAI)
1) Put your model files into `ai-service/models/`:
   - `dog_resnet50_120.pth`
   - `id2label_120.json` (e.g., {"0":"Beagle", ...} matching training order)
2) Edit `.env`:
   - `AI_MODE=real`
   - `MODEL_PTH_PATH=/app/models/dog_resnet50_120.pth`
   - `CLASS_MAP_PATH=/app/models/id2label_120.json`
   - `OPENAI_API_KEY=...`
3) Rebuild & run:
```bash
docker compose build
docker compose up -d
```

## Endpoints
- Frontend: `/`
- Public API (via Spring): `/api/v1/dogs/classify`, `/api/v1/dogs/search-similar`, `/api/v1/text/adoption-copy`
- AI Health: `/ai/health`
- Swagger: `/swagger`

## EC2 Practice (Single instance)
1. Launch **t3.large** (x86) in your region; open ports **80/22** (or use Session Manager instead of 22).
2. Install Docker & Compose:
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER && newgrp docker
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
docker compose version
```
3. Copy project to the instance and run:
```bash
unzip hackathon-template.zip -d ~/app
cd ~/app/hackathon-template
cp .env.example .env    # fill OPENAI_API_KEY etc.
docker compose build
docker compose up -d
```
4. Access `http://EC2_PUBLIC_IP/` from your browser.

> Tip: Use a fixed EBS gp3 (80~100GB) and keep `.env` private. For HTTPS, attach an ALB+ACM later, or add Let's Encrypt to Nginx.

## Notes
- For GPU, switch base images accordingly and run Compose with `--gpus all`.
- The similarity search (CLIP+FAISS) is wired for later enabling; prepare an index and update `ai_real.py`.
