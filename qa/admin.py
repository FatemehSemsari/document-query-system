from django.contrib import admin
from django.utils.text import Truncator

from .models import QuestionAnswer

import logging

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import AskQuestionForm
from .services import ask_and_save


logger = logging.getLogger(__name__)

@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'short_question',
        'short_answer',
        'user',
        'created_at'
    )

    search_fields = (
        'question',
        'answer',
        'user__username'
    )

    list_filter = (
        'created_at',
    )

    readonly_fields = (
        'user',
        'question',
        'answer',
        'sources',
        'created_at'
    )

    fields = readonly_fields

    ordering = ('-created_at', '-id')

    list_per_page = 20

    list_select_related = ('user',)

    def add_view(
            self,
            request,
            form_url='',
            extra_context=None
    ):

        if not self.has_add_permission(request):
            raise PermissionDenied

        form = AskQuestionForm(
            request.POST if request.method == 'POST' else None
        )

        if request.method == 'POST' and form.is_valid():

            try:
                history = ask_and_save(
                    question=form.cleaned_data['question'],
                    user=request.user
                )

            except Exception as exc:

                logger.error(
                    'Admin question failed: %s',
                    type(exc).__name__
                )

                form.add_error(
                    None,
                    'Failed to generate an answer. Please try again.'
                )

            else:

                self.message_user(
                    request,
                    'Question answered successfully.'
                )

                if self.has_view_permission(request, history):
                    return redirect(
                        reverse(
                            'admin:qa_questionanswer_change',
                            args=[history.pk]
                        )
                    )

                return redirect(reverse('admin:index'))

        context = {
            **self.admin_site.each_context(request),
            **(extra_context or {}),
            'opts': self.model._meta,
            'title': 'Ask a question',
            'form': form
        }

        return render(
            request,
            'admin/qa/ask_question.html',
            context
        )

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='Question')
    def short_question(self, obj):
        return Truncator(obj.question).chars(70)

    @admin.display(description='Answer')
    def short_answer(self, obj):
        return Truncator(obj.answer).chars(100)