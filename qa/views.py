import logging

from django.core.exceptions import ImproperlyConfigured

from groq import (
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    APIError
)

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from documents.retrieval import retrieve_documents

from .serializers import QuestionSerializer
from .rag_pipeline import answer_question


logger = logging.getLogger(__name__)


class AskQuestionView(GenericAPIView):

    serializer_class = QuestionSerializer

    def post(self, request):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data['question']

        try:
            result = answer_question(question)

        except RateLimitError:

            return Response(
                {
                    'error': 'LLM service rate limit exceeded.'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        except APITimeoutError:

            return Response(
                {
                    'error': 'LLM service request timed out.'
                },
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )

        except APIConnectionError:

            return Response(
                {
                    'error': 'Cannot connect to LLM service.'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        except APIError as exc:

            logger.error(
                'Groq error: %s',
                type(exc).__name__
            )

            return Response(
                {
                    'error': 'LLM service returned an error.'
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        except ImproperlyConfigured:

            return Response(
                {
                    'error': 'LLM service is not configured.'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        except Exception as exc:

            logger.error(
                'RAG pipeline error: %s',
                type(exc).__name__
            )

            return Response(
                {
                    'error': 'An internal error occurred.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            result,
            status=status.HTTP_200_OK
        )


class SearchDocumentsView(GenericAPIView):

    serializer_class = QuestionSerializer

    def post(self, request):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data['question']

        try:
            results = retrieve_documents(question)

            documents = []

            for doc, distance, rerank_score in results:

                documents.append({
                    'document_id': doc.metadata.get(
                        'document_id'
                    ),
                    'title': doc.metadata.get('title'),
                    'chunk_index': doc.metadata.get(
                        'chunk_index'
                    ),
                    'text': doc.page_content,
                    'distance': float(distance),
                    'rerank_score': float(rerank_score)
                })

        except Exception as exc:

            logger.error(
                'Retrieval error: %s',
                type(exc).__name__
            )

            return Response(
                {
                    'error': 'Document retrieval failed.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'question': question,
            'count': len(documents),
            'results': documents
        })