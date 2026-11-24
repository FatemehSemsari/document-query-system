import hashlib
from functools import lru_cache
from threading import RLock

from django.conf import settings

from langchain_chroma import Chroma
from langchain_core.documents import (
    Document as LangChainDocument
)

from .models import Document
from .embeddings import get_embedding_model
from .text_splitter import split_document


index_lock = RLock()


@lru_cache(maxsize=1)
def get_vector_store():
    return Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,

        embedding_function=get_embedding_model(),

        persist_directory=str(
            settings.CHROMA_DB_PATH
        )
    )


def build_chunks():
    chunks = {}

    documents = Document.objects.all().iterator()

    for document in documents:
        parts = split_document(document.full_text)

        for index, text in enumerate(parts):

            content = f'{document.title}\0{text}'

            fingerprint = hashlib.sha256(
                content.encode('utf-8')
            ).hexdigest()

            chunk_id = (
                f'{document.pk}:{index}:{fingerprint}'
            )

            chunks[chunk_id] = LangChainDocument(
                page_content=text,

                metadata={
                    'document_id': document.pk,
                    'title': document.title,
                    'chunk_index': index
                }
            )

    return chunks


def sync_vector_store():
    with index_lock:
        vector_store = get_vector_store()

        expected_chunks = build_chunks()

        existing_ids = set(
            vector_store.get(
                include=['metadatas']
            )['ids']
        )

        expected_ids = set(expected_chunks)

        new_ids = sorted(
            expected_ids - existing_ids
        )

        stale_ids = sorted(
            existing_ids - expected_ids
        )

        # Add new or changed chunks

        for start in range(0, len(new_ids), 100):
            batch = new_ids[start:start + 100]

            vector_store.add_documents(
                documents=[
                    expected_chunks[chunk_id]
                    for chunk_id in batch
                ],
                ids=batch
            )

        # Remove deleted or outdated chunks

        for start in range(0, len(stale_ids), 100):
            batch = stale_ids[start:start + 100]

            vector_store.delete(ids=batch)

        return {
            'total': len(expected_ids),
            'added': len(new_ids),
            'removed': len(stale_ids)
        }


def semantic_search(question, k=3):
    if not question or not question.strip():
        return []

    if k <= 0:
        return []

    with index_lock:
        stats = sync_vector_store()

        if stats['total'] == 0:
            return []

        vector_store = get_vector_store()

        return vector_store.similarity_search_with_score(
            query=question.strip(),
            k=min(k, stats['total'])
        )