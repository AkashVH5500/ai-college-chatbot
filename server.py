"""FastAPI backend for a Gemini-powered college FAQ assistant."""

import json
import os
from pathlib import Path
from typing import List

import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
FAQ_FILE = BASE_DIR / "faqs.json"

load_dotenv(BASE_DIR / ".env")
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Create a local .env from .env.example.")

genai.configure(api_key=API_KEY)

CHAT_MODEL = "models/gemini-1.5-flash-latest"
EMBED_MODEL = "models/text-embedding-004"


class FAQPayload(BaseModel):
    question: str
    answer: str


class FAQItem(FAQPayload):
    id: int


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    top_faqs: List[FAQItem]


app = FastAPI(title="College Assistant Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

faq_list: List[FAQItem] = []
faq_embeddings: List[np.ndarray] = []


def faq_to_dict(item: FAQItem) -> dict:
    if hasattr(item, "model_dump"):
        return item.model_dump()
    return item.dict()


def load_faqs() -> None:
    """Load FAQs from disk and assign stable IDs to entries without one."""
    global faq_list

    if not FAQ_FILE.exists():
        FAQ_FILE.write_text(json.dumps({"faqs": []}, indent=2), encoding="utf-8")
        faq_list = []
        return

    data = json.loads(FAQ_FILE.read_text(encoding="utf-8"))
    rows = data.get("faqs", [])
    if not isinstance(rows, list):
        raise ValueError("faqs.json must contain a 'faqs' array.")

    loaded: List[FAQItem] = []
    used_ids = set()
    next_id = 1

    for row in rows:
        if not isinstance(row, dict):
            continue
        question = str(row.get("question", "")).strip()
        answer = str(row.get("answer", "")).strip()
        if not question or not answer:
            continue

        try:
            faq_id = int(row.get("id", next_id))
        except (TypeError, ValueError):
            faq_id = next_id

        while faq_id in used_ids:
            faq_id += 1

        loaded.append(FAQItem(id=faq_id, question=question, answer=answer))
        used_ids.add(faq_id)
        next_id = max(next_id, faq_id + 1)

    faq_list = loaded


def save_faqs() -> None:
    payload = {"faqs": [faq_to_dict(item) for item in faq_list]}
    FAQ_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def embed_text(text: str) -> np.ndarray:
    response = genai.embed_content(model=EMBED_MODEL, content=text)
    return np.asarray(response["embedding"], dtype=np.float32)


def rebuild_embeddings() -> None:
    global faq_embeddings
    faq_embeddings = [embed_text(item.question) for item in faq_list]


def semantic_search(query: str, top_k: int = 3, threshold: float = 0.60) -> List[FAQItem]:
    if not faq_list:
        return []

    if len(faq_embeddings) != len(faq_list):
        rebuild_embeddings()

    query_embedding = embed_text(query)
    scored = []

    for faq, embedding in zip(faq_list, faq_embeddings):
        denominator = float(np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
        if denominator == 0:
            continue
        score = float(np.dot(query_embedding, embedding) / denominator)
        if score >= threshold:
            scored.append((faq, score))

    scored.sort(key=lambda row: row[1], reverse=True)
    return [faq for faq, _ in scored[:top_k]]


@app.on_event("startup")
def startup() -> None:
    load_faqs()
    if faq_list:
        rebuild_embeddings()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/faqs", response_model=List[FAQItem])
def get_all_faqs():
    return faq_list


@app.post("/faqs", response_model=FAQItem)
def add_faq(payload: FAQPayload):
    question = payload.question.strip()
    answer = payload.answer.strip()
    if not question or not answer:
        raise HTTPException(status_code=400, detail="Question and answer are required.")

    embedding = embed_text(question)
    new_id = max((item.id for item in faq_list), default=0) + 1
    item = FAQItem(id=new_id, question=question, answer=answer)
    faq_list.append(item)
    faq_embeddings.append(embedding)
    save_faqs()
    return item


@app.put("/faqs/{faq_id}", response_model=FAQItem)
def update_faq(faq_id: int, payload: FAQPayload):
    question = payload.question.strip()
    answer = payload.answer.strip()
    if not question or not answer:
        raise HTTPException(status_code=400, detail="Question and answer are required.")

    for index, current in enumerate(faq_list):
        if current.id == faq_id:
            embedding = embed_text(question)
            updated = FAQItem(id=faq_id, question=question, answer=answer)
            faq_list[index] = updated
            if index < len(faq_embeddings):
                faq_embeddings[index] = embedding
            else:
                rebuild_embeddings()
            save_faqs()
            return updated

    raise HTTPException(status_code=404, detail="FAQ not found.")


@app.delete("/faqs/{faq_id}")
def delete_faq(faq_id: int):
    for index, current in enumerate(faq_list):
        if current.id == faq_id:
            faq_list.pop(index)
            if index < len(faq_embeddings):
                faq_embeddings.pop(index)
            else:
                rebuild_embeddings()
            save_faqs()
            return {"deleted": True, "id": faq_id}

    raise HTTPException(status_code=404, detail="FAQ not found.")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    matches = semantic_search(question)
    faq_context = "\n\n".join(
        f"Q: {item.question}\nA: {item.answer}" for item in matches
    ) or "No matching FAQ was found."

    model = genai.GenerativeModel(CHAT_MODEL)
    response = model.generate_content(
        "Answer the student's question using the college FAQ context below. "
        "Do not invent official dates, fees, contacts or policies. "
        "When the context does not contain the answer, say that the student "
        "should verify it with the college office.\n\n"
        f"Student question: {question}\n\nFAQ context:\n{faq_context}"
    )

    answer = getattr(response, "text", None) or (
        "The AI provider did not return a text response. Please try again."
    )
    return ChatResponse(answer=answer, top_faqs=matches)
