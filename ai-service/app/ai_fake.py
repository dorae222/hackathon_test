import random
from PIL import Image

BREEDS = ["Beagle","Chihuahua","Pug","Golden Retriever","Shih-Tzu"]

def classify_image(img: Image.Image, top_k: int = 5):
    scores = [random.random() for _ in BREEDS]
    pairs = sorted(zip(BREEDS, scores), key=lambda x:x[1], reverse=True)[:top_k]
    total = sum(x for _, x in pairs) or 1.0
    return [{"label": b, "score": s/total} for b, s in pairs]

def search_similar_images(img: Image.Image, top_k: int = 8):
    base = "/img/placeholder-dog.png"
    return [{"image_id": str(i), "breed": random.choice(BREEDS), "url": base, "similarity": round(1.0 - i*0.07, 2)} for i in range(top_k)]

def generate_copy(breed: str, traits: list, age: str|None, tone: str):
    t = ", ".join(traits) if traits else "사랑스러운 성격"
    a = age or "미상"
    return f"{breed} 친구({a}) — {t}. 따뜻한 가족을 기다리고 있어요!"
