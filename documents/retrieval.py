from django.conf import settings

from .vector_store import semantic_search
from .reranker import rerank_results


def retrieve_documents(question):

    # Initial semantic search

    results = semantic_search(
        question=question,
        k=settings.RETRIEVAL_TOP_K
    )

    # Rerank retrieved chunks

    ranked_results = rerank_results(
        question=question,
        results=results,
        top_k=settings.RAG_TOP_K
    )

    return ranked_results