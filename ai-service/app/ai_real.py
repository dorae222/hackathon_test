import os, json, torch
from PIL import Image
import torchvision.transforms as T
import torchvision.models as models
from openai import OpenAI

# ---------- env ----------
MODEL_PTH_PATH = os.getenv("MODEL_PTH_PATH", "/app/models/dog_resnet50_120.pth")
CLASS_MAP_PATH  = os.getenv("CLASS_MAP_PATH", "/app/models/id2label_120.json")
NUM_CLASSES     = int(os.getenv("NUM_CLASSES", "120"))
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL    = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------- classifier ----------
def _load_id2label():
    with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
        m = json.load(f)
    return {int(k): v for k, v in m.items()}

def _build_resnet50(num_classes: int):
    m = models.resnet50(weights=None)
    m.fc = torch.nn.Linear(m.fc.in_features, num_classes)
    return m

_id2label = _load_id2label()
_model = _build_resnet50(NUM_CLASSES)
_state = torch.load(MODEL_PTH_PATH, map_location="cpu")
_model.load_state_dict(_state, strict=False)
_model.eval().to(device)

_transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]),
])

@torch.inference_mode()
def classify_image(pil_img: Image.Image, top_k: int = 5):
    x = _transform(pil_img.convert("RGB")).unsqueeze(0).to(device)
    logits = _model(x)
    probs = torch.softmax(logits, dim=-1)[0]
    topv, topi = torch.topk(probs, k=top_k)
    return [{"label": _id2label[i.item()], "score": float(v)} for v, i in zip(topv, topi)]

# ---------- similarity (optional; CLIP+FAISS to be enabled when ready) ----------
def search_similar_images(pil_img: Image.Image, top_k: int = 8):
    return []

# ---------- OpenAI copy ----------
def generate_copy(breed: str, traits: list, age: str|None, tone: str):
    if not OPENAI_API_KEY:
        t = ", ".join(traits) if traits else "사랑스러운 성격"
        a = age or "미상"
        return f"{breed} — {t}. 새로운 가족을 만나길 기다립니다."
    client = OpenAI(api_key=OPENAI_API_KEY)
    instructions = (
        "너는 유기견 입양을 돕는 카피라이터다. 한국어로 1~2문장, 120자 이내, "
        "과장/의학적 단정 금지, 이모지는 1개 이하."
    )
    user = f"견종: {breed}\n특징: {', '.join(traits) if traits else '미상'}\n나이: {age or '미상'}\n톤: {tone}"
    res = client.responses.create(model=OPENAI_MODEL, instructions=instructions, input=user)
    text = getattr(res, "output_text", "").strip()
    return text or f"{breed} 친구가 새로운 가족을 기다리고 있어요."
