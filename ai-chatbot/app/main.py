import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="AI Chat Service")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    system_prompt: Optional[str] = None
    messages: List[ChatMessage]
    model: Optional[str] = None

def _build_client_and_model(model: Optional[str]):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=api_key)
    return client, (model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        client, model_name = _build_client_and_model(req.model)
        msgs = []
        if req.system_prompt:
            msgs.append({"role":"system","content":req.system_prompt})
        msgs.extend([m.model_dump() for m in req.messages])
        
        resp = client.chat.completions.create(model=model_name, messages=msgs)
        reply = resp.choices[0].message.content or ""
        
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")