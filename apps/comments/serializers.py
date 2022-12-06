from rest_framework import serializers

from db.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer
    """

    class Meta:
        model = Comment
        fields = [
            "user",
            "product",
            "subject",
            "content",
            "rate",
            "created_at",
        ]
