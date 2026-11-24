from functools import lru_cache

from django.conf import settings

from sentence_transformers import CrossEncoder


@lru_cache(maxsize=1)
def get_reranker():

    return CrossEncoder(
        settings.RERANKER_MODEL,
        device='cpu',
        max_length=512
    )


def rerank_results(question, results, top_k=4):

    if not results or top_k <= 0:
        return []

    reranker = get_reranker()

    pairs = [
        (question, doc.page_content)
        for doc, distance in results
    ]

    scores = reranker.predict(
        pairs,
        batch_size=8,
        show_progress_bar=False
    )

    ranked_results = []

    for (doc, distance), score in zip(
        results, scores
    ):

        ranked_results.append((
            doc,
            float(distance),
            float(score)
        ))

    ranked_results.sort(
        key=lambda item: item[2],
        reverse=True
    )

    return ranked_results[:top_k]