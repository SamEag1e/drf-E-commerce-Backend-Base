from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Comment, Reply
from .utils import censor_content


# ---------------------------------------------------------------------
class CommentReplyBaseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    content = serializers.SerializerMethodField()

    # -----------------------------------------------------------------
    def get_content(self, obj):
        request = self.context.get("request")
        if request and request.user.is_staff:
            return obj.content
        return censor_content(obj.content)

    # -----------------------------------------------------------------
    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Can not be empty")
        if len(value) > 500:
            raise serializers.ValidationError(
                "Lenght can not be more than 500 characters."
            )
        return value


# ---------------------------------------------------------------------
class ReplySerializer(CommentReplyBaseSerializer):
    comment = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all()
    )

    # -----------------------------------------------------------------
    class Meta:
        model = Reply
        fields = [
            "id",
            "user",
            "comment",
            "content",
            "is_visible",
            "created_at",
            "updated_at",
        ]


# ---------------------------------------------------------------------
class CommentSerializer(CommentReplyBaseSerializer):
    replies = ReplySerializer(many=True, read_only=True)

    # -----------------------------------------------------------------
    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "content",
            "is_visible",
            "created_at",
            "updated_at",
            "replies",
        ]
