from django.urls import path

from .views import (
    AskQuestionView,
    SearchDocumentsView
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