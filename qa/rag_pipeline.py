from langchain_core.output_parsers import StrOutputParser

from documents.retrieval import retrieve_documents

from .llm import get_llm
from .prompts import RAG_PROMPT, NO_ANSWER


def build_context(results):

    context_parts = []

    for index, (doc, distance, rerank_score) in enumerate(
        results, start=1
    ):

        title = doc.metadata.get('title', 'Unknown')

        context_parts.append(
            f"Source [{index}]\n"
            f"Document: {title}\n"
            f"Content:\n{doc.page_content}"
        )

    return "\n\n".join(context_parts)


def build_sources(results):

    sources = []

    for index, (doc, distance, rerank_score) in enumerate(
        results, start=1
    ):

        sources.append({
            'source_number': index,
            'document_id': doc.metadata.get('document_id'),
            'title': doc.metadata.get('title'),
            'chunk_index': doc.metadata.get('chunk_index'),
            'distance': float(distance),
            'rerank_score': float(rerank_score)
        })

    return sources


def answer_question(question):

    if not question or not question.strip():
        raise ValueError('Question cannot be empty.')

    question = question.strip()

    # Advanced document retrieval

    results = retrieve_documents(question)

    # Check retrieval results

    if not results:
        return {
            'question': question,
            'answer': NO_ANSWER,
            'sources': []
        }

    # Prepare context and sources

    context = build_context(results)

    sources = build_sources(results)

    # Load language model

    llm = get_llm()

    # Create LangChain pipeline

    chain = (
        RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    # Generate answer

    answer = chain.invoke({
        'context': context,
        'question': question
    }).strip()

    if not answer:
        raise RuntimeError(
            'The language model returned an empty answer.'
        )

    # Return result

    return {
        'question': question,
        'answer': answer,
        'sources': sources
    }