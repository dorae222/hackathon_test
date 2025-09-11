# 🐶 Hackathon Test Project

Spring Boot (Gateway) + FastAPI (AI) + Nginx (Frontend Proxy) + Bootstrap UI + Docker Compose

---

## 📌 Overview
해커톤 시연을 위해 빠르게 구축한 풀스택 템플릿입니다.  
**주요 기능:**
1. 사진 업로드 → PyTorch `.pth` 모델로 품종 분류
2. 스케치/사진 업로드 → 유사 이미지 검색 (CLIP+FAISS 확장 가능)
3. 견종/특징 입력 → OpenAI API 활용 입양 추천 문구 생성

---

## 🚀 Quickstart

### Windows (PowerShell 기준)

#### 1. 필수 설치
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) 설치
- 설치 후 Docker Desktop 실행
- 정상 동작 확인:
   ```powershell
   docker --version
   docker compose version
   ```

#### 2. 저장소 클론

```powershell
git clone https://github.com/dorae222/hackathon_test.git
cd hackathon_test
```

#### 3. 환경 변수 파일 생성

```powershell
copy .env.example .env
```

* 처음에는 `AI_MODE=fake`로 시작하세요

#### 4. 빌드 & 실행

```powershell
docker compose build
docker compose up -d
```

#### 5. 접속

* Frontend: [http://localhost/](http://localhost/)
* Swagger (Spring): [http://localhost:8080/swagger](http://localhost:8080/swagger)
* FastAPI Health: [http://localhost:8000/health](http://localhost:8000/health)

---

### Mac (zsh/bash 기준)

#### 1. 필수 설치

* [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/) 설치
* 정상 동작 확인:

   ```bash
   docker --version
   docker compose version
   ```

#### 2. 저장소 클론

```bash
git clone https://github.com/dorae222/hackathon_test.git
cd hackathon_test
```

#### 3. 환경 변수 파일 생성

```bash
cp .env.example .env
```

* 처음에는 `AI_MODE=fake`로 시작하세요

#### 4. 빌드 & 실행

```bash
docker compose build
docker compose up -d
```

#### 5. 접속

* Frontend: [http://localhost/](http://localhost/)
* Swagger (Spring): [http://localhost:8080/swagger](http://localhost:8080/swagger)
* FastAPI Health: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🔧 Modes

* `AI_MODE=fake` → 빠른 시연용 (랜덤 응답)
* `AI_MODE=real` → 실제 모델(.pth) + OpenAI API 사용

### Real Mode 전환

1. `ai-service/models/` 폴더에 파일 추가:
    * `dog_resnet50_120.pth`
    * `id2label_120.json`
2. `.env` 수정:
    ```env
    AI_MODE=real
    OPENAI_API_KEY=sk-xxxx
    ```
3. AI 서비스 재빌드:
    ```bash
    docker compose up -d --build ai
    ```

---

## ☁️ AWS EC2 연습

1. t3.large 인스턴스 생성 (포트 80/22 오픈)
2. Docker & Compose 설치:
    ```bash
    curl -fsSL https://get.docker.com | sh
    ```
3. 프로젝트 복사 후 실행:
    ```bash
    docker compose build
    docker compose up -d
    ```
4. 접속: `http://<EC2_PUBLIC_IP>/`

---

## 📝 명령어 요약

| 목적           | Windows PowerShell           | Mac (zsh/bash)              |
| -------------- | --------------------------- | --------------------------- |
| .env 파일 생성 | `copy .env.example .env`    | `cp .env.example .env`      |
| 빌드           | `docker compose build`      | `docker compose build`      |
| 실행           | `docker compose up -d`      | `docker compose up -d`      |
| 상태 확인      | `docker ps`                 | `docker ps`                 |
| 로그 확인      | `docker compose logs -f ai` | `docker compose logs -f ai` |
| 컨테이너 중지  | `docker compose down`       | `docker compose down`       |

---

## 🙌 Credits

* Backend: Spring Boot
* AI Service: FastAPI + PyTorch + OpenAI
* Frontend: Bootstrap 5
* Infra: Docker Compose, Nginx
