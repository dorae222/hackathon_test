import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from openai import OpenAI
import httpx

app = FastAPI(title="AI Chat Service")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    system_prompt: Optional[str] = None
    messages: List[ChatMessage]
    model: Optional[str] = None


class ChatByAnimalRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None

def _build_client_and_model(model: Optional[str]):
    """
    Returns (client, model_name, is_fake)
    - If OPENAI_API_KEY is missing, returns (None, "local-fake", True)
    - Otherwise returns real OpenAI client.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Dev-friendly fallback to keep UI working without external key
        return None, "local-fake", True
    client = OpenAI(api_key=api_key)
    return client, (model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")), False

def _vision_base_url() -> str:
    # When running in docker-compose, the service name resolves in the bridge network
    return os.getenv("AI_VISION_BASE_URL", "http://ai-vision:8000")

def _extract_field(info_list, key: str) -> str:
    if not info_list:
        return ""
    # info is like [[k,v,k2,v2], ...]
    for row in info_list:
        if not isinstance(row, list):
            continue
        if len(row) >= 2 and row[0] == key:
            return row[1] or ""
        if len(row) >= 4 and row[2] == key:
            return row[3] or ""
    return ""


def _fake_llm_reply(messages: List[dict], system_prompt: Optional[str] = None) -> str:
    """Very small local stub to simulate an assistant in dev.
    Echoes the last user message with a friendly Korean persona.
    """
    user_text = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            user_text = m.get("content", "")
            break
    intro = "안녕하세요, 반가워요! 저는 임시 챗봇이에요(오프라인 모드). "
    if system_prompt:
        intro += "(프로필 기반 답변을 흉내 내는 중) "
    if not user_text:
        return intro + "무엇이든 편하게 물어보세요. 멍! 🐶"
    return (
        f"{intro}방금 이렇게 말씀하셨어요: '{user_text}'. "
        "지금은 간단한 데모 모드라 상세한 답변은 어렵지만, 필요한 주제를 더 알려주시면 최대한 도와볼게요! 🐾"
    )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        client, model_name, is_fake = _build_client_and_model(req.model)
        msgs = []
        if req.system_prompt:
            msgs.append({"role":"system","content":req.system_prompt})
        msgs.extend([m.model_dump() for m in req.messages])
        if is_fake:
            reply = _fake_llm_reply(msgs, req.system_prompt)
        else:
            resp = client.chat.completions.create(model=model_name, messages=msgs)
            reply = resp.choices[0].message.content or ""
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")


@app.post("/chat/animal/{animal_id}")
async def chat_by_animal(animal_id: int = Path(..., ge=0), req: ChatByAnimalRequest = None):
    """
    Chat endpoint that builds the system prompt on the server using
    the animal profile fetched from ai-vision. Frontend should not send
    any system prompt.
    """
    try:
        # 1) Fetch animal profile
        async with httpx.AsyncClient(timeout=10.0) as client_http:
            resp = await client_http.get(f"{_vision_base_url()}/animals/{animal_id}")
            resp.raise_for_status()
            animal = resp.json()

        info = animal.get("info", [])
        dog_name = _extract_field(info, "이름") or "이름 미상"
        breed = _extract_field(info, "품종") or "-"
        age = _extract_field(info, "나이(추정)") or "-"
        gender = _extract_field(info, "성별") or "-"
        weight = _extract_field(info, "무게") or "-"
        color = _extract_field(info, "털색") or "-"
        status = _extract_field(info, "상태") or "-"
        serial = _extract_field(info, "일련번호") or "-"
        notes = _extract_field(info, "특이사항") or "-"

        profile_lines = "\n".join([
            f"이름: {dog_name}",
            f"품종: {breed}",
            f"나이(추정): {age}",
            f"성별: {gender}",
            f"무게: {weight}",
            f"털색: {color}",
            f"상태: {status}",
            f"일련번호: {serial}",
            f"특이사항: {notes}",
        ])

        region = os.getenv("SERVICE_REGION", "광주")
        preferred_domains = os.getenv("PREFERRED_DOMAINS", "kcanimal.or.kr")

        system_prompt = "\n".join([
            f"당신은 {region}시 유기견 보호소의 반려견 챗봇입니다.",
            "아래 프로필 정보에 기반하여 정중한 한국어로 답하고, 모르는 정보는 모른다고 답하세요.",
            "가능하면 친근한 강아지 말투(멍멍, 왈왈)를 사용하되 과하지 않게 해주세요.",
            f"링크나 참고자료를 언급할 경우 다음 도메인을 우선적으로 고려하세요: {preferred_domains}",
            "프로필에 없는 사실을 지어내지 마세요.",
            "대화가 충분히 진행되어 사용자가 추천서를 요청하거나 합의하면, 반드시 '추천서:'로 시작하는 단락 하나를 생성해 주세요.",
            "그 단락에는 입양자 라이프스타일 요약(대화에서 추출), 반려견의 강점, 주의사항, 첫 일주일 적응 팁을 간결히 포함하세요.",
            "",
            "[반려견 프로필]",
            profile_lines,
        ])

        # 2) Call OpenAI
        client, model_name, is_fake = _build_client_and_model(req.model if req else None)
        msgs = [{"role": "system", "content": system_prompt}]
        if req and req.messages:
            msgs.extend([m.model_dump() for m in req.messages])

        if is_fake:
            reply = _fake_llm_reply(msgs, system_prompt)
        else:
            resp = client.chat.completions.create(model=model_name, messages=msgs)
            reply = resp.choices[0].message.content or ""
        return {"reply": reply}
    except httpx.HTTPError as he:
        raise HTTPException(status_code=502, detail=f"Failed to fetch animal profile: {he}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat (animal) failed: {e}")