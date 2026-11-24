from functools import lru_cache

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from langchain_groq import ChatGroq


@lru_cache(maxsize=1)
def get_llm():

    if not settings.GROQ_API_KEY:
        raise ImproperlyConfigured(
            'GROQ_API_KEY is not configured.'
        )

    return ChatGroq(
        model=settings.GROQ_MODEL,

        api_key=settings.GROQ_API_KEY,

        temperature=settings.LLM_TEMPERATURE,

        timeout=60,

        max_retries=2
    )