from rest_framework import serializers


class QuestionSerializer(serializers.Serializer):

    question = serializers.CharField(
        max_length=1000,
        min_length=1,
        allow_blank=False,
        trim_whitespace=True
    )