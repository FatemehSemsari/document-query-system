from rest_framework import serializers

from .models import QuestionAnswer


class QuestionSerializer(serializers.Serializer):

    question = serializers.CharField(
        max_length=1000,
        min_length=1,
        allow_blank=False,
        trim_whitespace=True
    )


class QuestionAnswerSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='user.username',
        read_only=True,
        default=None
    )

    class Meta:

        model = QuestionAnswer

        fields = (
            'id',
            'user',
            'username',
            'question',
            'answer',
            'sources',
            'created_at'
        )

        read_only_fields = fields