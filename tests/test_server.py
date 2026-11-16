import json
import os
from types import SimpleNamespace

os.environ.setdefault("GEMINI_API_KEY", "ci-test-key")

import numpy as np
import pytest
from fastapi import HTTPException

import server


def test_admin_token_accepts_only_matching_bearer_token(monkeypatch):
    monkeypatch.setattr(server, "ADMIN_API_TOKEN", "expected-token")
    assert server.require_admin("Bearer expected-token") is None

    with pytest.raises(HTTPException) as exc:
        server.require_admin("Bearer wrong-token")
    assert exc.value.status_code == 401

    with pytest.raises(HTTPException) as exc:
        server.require_admin("Basic expected-token")
    assert exc.value.status_code == 401


def test_admin_mutation_routes_require_admin_dependency():
    route = next(
        item
        for item in server.app.routes
        if getattr(item, "path", None) == "/faqs"
        and "POST" in getattr(item, "methods", set())
    )
    assert any(
        dependency.call is server.require_admin
        for dependency in route.dependant.dependencies
    )


def test_load_faqs_assigns_unique_ids_and_skips_invalid_rows(tmp_path, monkeypatch):
    faq_file = tmp_path / "faqs.json"
    faq_file.write_text(
        json.dumps(
            {
                "faqs": [
                    {"id": 4, "question": "Fees", "answer": "Check the office"},
                    {"id": 4, "question": "Library", "answer": "Check the library"},
                    {"question": "Invalid", "answer": "   "},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(server, "FAQ_FILE", faq_file)

    server.load_faqs()

    assert [item.id for item in server.faq_list] == [4, 5]
    assert [item.question for item in server.faq_list] == ["Fees", "Library"]


def test_rebuild_embeddings_batches_faq_questions(monkeypatch):
    server.faq_list = [
        server.FAQItem(id=1, question="Fees", answer="Check office"),
        server.FAQItem(id=2, question="Library", answer="Check library"),
    ]

    class FakeModels:
        def __init__(self):
            self.kwargs = None

        def embed_content(self, **kwargs):
            self.kwargs = kwargs
            return SimpleNamespace(
                embeddings=[
                    SimpleNamespace(values=[1.0, 0.0]),
                    SimpleNamespace(values=[0.0, 1.0]),
                ]
            )

    fake_models = FakeModels()
    monkeypatch.setattr(server, "client", SimpleNamespace(models=fake_models))

    server.rebuild_embeddings()

    assert fake_models.kwargs["contents"] == ["Fees", "Library"]
    assert len(server.faq_embeddings) == 2
    assert server.faq_embeddings[0].dtype == np.float32


def test_semantic_search_ranks_matches_by_cosine_similarity(monkeypatch):
    server.faq_list = [
        server.FAQItem(id=1, question="First", answer="A"),
        server.FAQItem(id=2, question="Second", answer="B"),
    ]
    server.faq_embeddings = [
        np.asarray([1.0, 0.0], dtype=np.float32),
        np.asarray([0.0, 1.0], dtype=np.float32),
    ]
    monkeypatch.setattr(
        server,
        "embed_text",
        lambda _text: np.asarray([0.8, 0.6], dtype=np.float32),
    )

    results = server.semantic_search("query", threshold=0.5)

    assert [item.id for item in results] == [1, 2]


def test_add_faq_persists_valid_entry(tmp_path, monkeypatch):
    faq_file = tmp_path / "faqs.json"
    monkeypatch.setattr(server, "FAQ_FILE", faq_file)
    monkeypatch.setattr(server, "faq_list", [])
    monkeypatch.setattr(server, "faq_embeddings", [])
    monkeypatch.setattr(
        server,
        "embed_text",
        lambda _text: np.asarray([0.25, 0.75], dtype=np.float32),
    )

    created = server.add_faq(server.FAQPayload(question="Library", answer="Ask the office"))

    saved = json.loads(faq_file.read_text(encoding="utf-8"))
    assert created.id == 1
    assert saved["faqs"][0]["question"] == "Library"
    assert saved["faqs"][0]["id"] == 1


def test_add_faq_rejects_empty_fields():
    with pytest.raises(HTTPException) as exc:
        server.add_faq(server.FAQPayload(question="  ", answer="Answer"))
    assert exc.value.status_code == 400


def test_require_admin_is_disabled_without_server_token(monkeypatch):
    monkeypatch.setattr(server, "ADMIN_API_TOKEN", None)
    with pytest.raises(HTTPException) as exc:
        server.require_admin("Bearer any-token")
    assert exc.value.status_code == 503
