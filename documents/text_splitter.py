from functools import lru_cache

from django.conf import settings
from transformers import AutoTokenizer
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)


@lru_cache(maxsize=1)
def get_text_splitter():
    tokenizer = AutoTokenizer.from_pretrained(settings.EMBEDDING_MODEL)

    return (
        RecursiveCharacterTextSplitter
        .from_huggingface_tokenizer(
            tokenizer,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=[
                '\n\n',
                '\n',
                ' ',
                ''
            ]
        )
    )


def split_document(text):
    if not text or not text.strip():
        return []

    splitter = get_text_splitter()

    return splitter.split_text(text)