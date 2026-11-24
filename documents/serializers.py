from zipfile import BadZipFile

from rest_framework import serializers

from docx.opc.exceptions import PackageNotFoundError
from lxml.etree import XMLSyntaxError

from .models import Document
from .services import extract_docx_text


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document

        fields = (
            'id',
            'title',
            'file',
            'full_text',
            'created_at',
            'updated_at'
        )

        read_only_fields = (
            'id',
            'full_text',
            'created_at',
            'updated_at'
        )

    def validate_file(self, file):

        if not file.name.lower().endswith('.docx'):
            raise serializers.ValidationError(
                'Only DOCX files are allowed.'
            )

        if file.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                'File size cannot exceed 10 MB.'
            )

        return file

    def validate(self, attrs):

        file = attrs.get('file')

        if file is not None:

            try:
                full_text = extract_docx_text(file)

            except (
                BadZipFile,
                PackageNotFoundError,
                XMLSyntaxError,
                ValueError,
                KeyError,
                OSError
            ):
                raise serializers.ValidationError({
                    'file': 'Invalid or corrupted DOCX file.'
                })

            if not full_text:
                raise serializers.ValidationError({
                    'file': 'Document contains no readable text.'
                })

            attrs['full_text'] = full_text

        return attrs