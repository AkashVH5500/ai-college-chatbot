"""
FastAPI backend for College Chatbot (Gemini API Version)
- FAQ storage (faqs.json)
- Embeddings (Gemini)
- Semantic search
- Chat with FAQ context
"""

import os
import json
from typing import List
import numpy as np

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# -----------------------------
# Gemini library
# -----------------------------
import google.generativeai as genai

# -----------------------------
# Load environment
# -----------------------------
from dotenv import load_dotenv
import pathlib

env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

genai.configure(api_key=API_KEY)

# -----------------------------
# Gemini Models
# -----------------------------
CHAT_MODEL = "models/gemini-1.5-flash-latest"  # Fixed format
EMBED_MODEL = "models/text-embedding-004"      # Already correct

# -----------------------------
# File path
# -----------------------------
FAQ_FILE = "faqs.json"

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="College Chatbot Backend (Gemini Edition)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Pydantic Models
# -----------------------------
class FAQItem(BaseModel):
    question: str
    answer: str

class FAQWithScore(FAQItem):
    score: float

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    top_faqs: List[FAQWithScore]


# -----------------------------
# In-memory storage
# -----------------------------
faq_list: List[FAQItem] = []
faq_embeddings: List[np.ndarray] = []

# -----------------------------
# File Functions
# -----------------------------
def load_faqs():
    global faq_list

    if not os.path.exists(FAQ_FILE):
        with open(FAQ_FILE, "w") as f:
            json.dump({"faqs": []}, f, indent=2)
        faq_list = []
        return

    with open(FAQ_FILE, "r") as f:
        data = json.load(f)

    faq_list = [FAQItem(**x) for x in data.get("faqs", [])]


def save_faqs():
    with open(FAQ_FILE, "w") as f:
        json.dump({"faqs": [f.model_dump() for f in faq_list]}, f, indent=2)


# -----------------------------
# Embeddings
# -----------------------------
def embed_text(text: str) -> np.ndarray:
    """Generate embeddings using Gemini."""
    res = genai.embed_content(
        model=EMBED_MODEL,
        content=text
    )
    return np.array(res["embedding"], dtype="float32")


def rebuild_embeddings():
    global faq_embeddings
    faq_embeddings = [embed_text(f.question) for f in faq_list]


# -----------------------------
# Semantic Search
# -----------------------------
def semantic_search(query: str, top_k: int = 3, threshold: float = 0.60):
    if not faq_list:
        return []

    q_emb = embed_text(query)

    scored = []
    for faq, emb in zip(faq_list, faq_embeddings):
        score = float(np.dot(q_emb, emb) / (np.linalg.norm(q_emb) * np.linalg.norm(emb)))
        scored.append((faq, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    matches = [
        FAQWithScore(question=f.question, answer=f.answer, score=s)
        for f, s in scored[:top_k]
        if s >= threshold
    ]

    return matches


# -----------------------------
# Startup
# -----------------------------
@app.on_event("startup")
def startup():
    load_faqs()
    if faq_list:
        rebuild_embeddings()


# -----------------------------
# Routes
# -----------------------------
@app.get("/faqs", response_model=List[FAQItem])
def get_all_faqs():
    return faq_list


@app.post("/faqs", response_model=FAQItem)
def add_faq(item: FAQItem):
    faq_list.append(item)
    save_faqs()
    faq_embeddings.append(embed_text(item.question))
    return item


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    question = req.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Empty question")

    matches = semantic_search(question)

    if matches:
        context = "\n".join([f"Q: {m.question}\nA: {m.answer}" for m in matches])
    else:
        context = "No similar FAQ found."

    # Gemini chat
    model = genai.GenerativeModel(CHAT_MODEL)
    response = model.generate_content(
        f"User question: {question}\n\nRelevant FAQ answers:\n{context}\n\nProvide the best possible answer:"
    )

    answer = response.text if hasattr(response, "text") else "No response"

    return ChatResponse(answer=answer, top_faqs=matches)
