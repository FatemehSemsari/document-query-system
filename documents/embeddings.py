from functools import lru_cache

from django.conf import settings
from langchain_huggingface import HuggingFaceEmbeddings


@lru_cache(maxsize=1)
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,

        model_kwargs={
            'device': 'cpu'
        },

        encode_kwargs={
            'normalize_embeddings': True,
            'prompt': 'passage: '
        },

        query_encode_kwargs={
            'normalize_embeddings': True,
            'prompt': 'query: '
        }
    )