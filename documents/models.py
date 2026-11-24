from django.db import models
from django.core.validators import FileExtensionValidator


class Document(models.Model):
    title = models.CharField(max_length=255)

    file = models.FileField(
        upload_to='documents/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['docx']
            )
        ]
    )

    full_text = models.TextField(
        blank=True,
        editable=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title