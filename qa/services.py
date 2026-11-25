from .models import QuestionAnswer
from .rag_pipeline import answer_question


def ask_and_save(question, user=None):

    result = answer_question(question)

    history = QuestionAnswer.objects.create(
        user=user,
        question=result['question'],
        answer=result['answer'],
        sources=result['sources']
    )

    return history