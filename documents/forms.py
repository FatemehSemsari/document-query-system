from zipfile import BadZipFile

from django import forms
from django.core.files.uploadedfile import UploadedFile
from docx.opc.exceptions import PackageNotFoundError
from lxml.etree import XMLSyntaxError

from .models import Document
from .services import extract_docx_text


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ['title', 'file']

    def clean_file(self):
        file = self.cleaned_data['file']

        if isinstance(file, UploadedFile):

            if not file.name.lower().endswith('.docx'):
                raise forms.ValidationError(
                    'Only DOCX files are allowed.'
                )

            try:
                self.extracted_text = extract_docx_text(file)

            except (
                BadZipFile,
                PackageNotFoundError,
                XMLSyntaxError,
                ValueError,
                KeyError,
                OSError
            ):
                raise forms.ValidationError(
                    'Invalid or corrupted DOCX file.'
                )

            if not self.extracted_text:
                raise forms.ValidationError(
                    'The document contains no readable text.'
                )

        return file

    def save(self, commit=True):
        if hasattr(self, 'extracted_text'):
            self.instance.full_text = self.extracted_text

        return super().save(commit=commit)