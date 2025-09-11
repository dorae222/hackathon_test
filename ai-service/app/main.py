import os, io, time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from app.util import json_err

AI_MODE = os.getenv("AI_MODE", "fake").lower()

if AI_MODE == "real":
    from app.ai_real import classify_image, search_similar_images, generate_copy
else:
    from app.ai_fake import classify_image, search_similar_images, generate_copy
    
app = FastAPI(title="AI Service", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(): return {"status":"ok","mode":AI_MODE}

@app.post("/v1/classify")
async def classify(file: UploadFile = File(...), top_k: int = int(os.getenv("TOPK", "5"))):
    try:
        img = Image.open(io.BytesIO(await file.read()))
        t0 = time.time()
        preds = classify_image(img, top_k)
        return {"top1": preds[0], "topk": preds, "inference_ms": int((time.time()-t0)*1000)}
    except Exception as e:
        raise HTTPException(400, json_err("classify_failed", str(e)))

@app.post("/v1/search/similar")
async def similar(file: UploadFile = File(...), top_k: int = 8):
    try:
        img = Image.open(io.BytesIO(await file.read()))
        results = search_similar_images(img, top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(400, json_err("search_failed", str(e)))

@app.post("/v1/generate/adoption-copy")
async def copy(payload: dict):
    breed = payload.get("breed")
    if not breed:
        raise HTTPException(400, json_err("bad_request", "breed required"))
    text = generate_copy(breed, payload.get("traits", []), payload.get("age"), payload.get("tone","따뜻하고 간결"))
    return {"copy": text}
