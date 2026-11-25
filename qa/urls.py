from django.urls import path

from rest_framework.routers import SimpleRouter

from .views import (
    AskQuestionView,
    SearchDocumentsView,
    QuestionAnswerViewSet
)


router = SimpleRouter()

router.register(
    r'history',
    QuestionAnswerViewSet,
    basename='history'
)


urlpatterns = [

    path(
        'ask/',
        AskQuestionView.as_view(),
        name='ask-question'
    ),

    path(
        'search/',
        SearchDocumentsView.as_view(),
        name='search-documents'
    ),

]

urlpatterns += router.urls