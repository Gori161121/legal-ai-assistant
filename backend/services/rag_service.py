"""
Retrieval (RAG) Service

Answers general client questions by retrieving the most relevant entries from
the firm's legal FAQ knowledge base, using a dependency-free TF-IDF cosine
ranking. The retrieved text is general information, NOT legal advice.
"""
from __future__ import annotations

import math
import re
from collections import Counter

DISCLAIMER = "This is general information, not legal advice."


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z]+", (text or "").lower())


def _build_index(docs: list) -> tuple[list, Counter, int]:
    corpus = [_tokenize(f"{d['question']} {d['answer']} {d.get('topic', '')}") for d in docs]
    df: Counter = Counter()
    for tokens in corpus:
        for token in set(tokens):
            df[token] += 1
    return corpus, df, len(docs)


def _tfidf_vector(tokens: list[str], df: Counter, n_docs: int) -> dict:
    tf = Counter(tokens)
    vec = {}
    for token, count in tf.items():
        idf = math.log((n_docs + 1) / (df.get(token, 0) + 1)) + 1
        vec[token] = count * idf
    return vec


def _cosine(a: dict, b: dict) -> float:
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values())) or 1.0
    nb = math.sqrt(sum(v * v for v in b.values())) or 1.0
    return dot / (na * nb)


def retrieve(query: str, docs: list, k: int = 3) -> dict:
    corpus, df, n_docs = _build_index(docs)
    query_vec = _tfidf_vector(_tokenize(query), df, n_docs)

    scored = []
    for i, tokens in enumerate(corpus):
        score = _cosine(query_vec, _tfidf_vector(tokens, df, n_docs))
        if score > 0:
            scored.append((score, i))
    scored.sort(reverse=True)

    results = [{
        "score": round(score, 3),
        "topic": docs[i]["topic"],
        "question": docs[i]["question"],
        "answer": docs[i]["answer"],
    } for score, i in scored[:k]]

    return {
        "query": query,
        "results": results,
        "answer": results[0]["answer"] if results else
                  "I don't have information on that yet — a lawyer can help at your consultation.",
        "disclaimer": DISCLAIMER,
    }
