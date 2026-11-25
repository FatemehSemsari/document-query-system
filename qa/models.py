from django.conf import settings
from django.db import models


class QuestionAnswer(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions'
    )

    question = models.TextField()

    answer = models.TextField()

    sources = models.JSONField(
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = 'Question and Answer'
        verbose_name_plural = 'Questions and Answers'

    def __str__(self):
        return self.question[:80]