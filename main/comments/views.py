from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import (
    NotFound,
    ValidationError,
    PermissionDenied,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from .models import Comment, Reply
from .serializers import CommentSerializer, ReplySerializer


# ---------------------------------------------------------------------
class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # -----------------------------------------------------------------
    @action(detail=False, methods=["get"])
    def related(self, request):
        content_type = request.query_params.get("content_type")
        object_id = request.query_params.get("object_id")

        if not content_type or not object_id:
            raise ValidationError(
                "Both 'content_type' and 'object_id' are required."
            )

        content_type_instance = get_object_or_404(
            ContentType, model=content_type.lower()
        )
        comments = Comment.objects.filter(
            content_type=content_type_instance,
            object_id=object_id,
            is_visible=True,
        )
        if not comments.exists():
            raise NotFound(
                "No comments found for the given content type and object ID"
            )

        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    # -----------------------------------------------------------------
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to add a comment.")

        content_type = self.request.data.get("content_type")
        object_id = self.request.data.get("object_id")
        if not content_type or not object_id:
            raise ValidationError(
                "Both 'content_type' and 'object_id' are required."
            )

        content_type_instance = get_object_or_404(
            ContentType, model=content_type.lower()
        )
        serializer.save(
            user=self.request.user,
            content_type=content_type_instance,
            object_id=object_id,
        )

    # -----------------------------------------------------------------
    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.user != self.request.user:
            raise PermissionDenied("You can only edit your own comments.")
        serializer.save()


# ---------------------------------------------------------------------
class ReplyViewSet(ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # -----------------------------------------------------------------
    def perform_create(self, serializer):
        comment_id = self.request.data.get("comment")
        comment = Comment.objects.get(id=comment_id)
        serializer.save(user=self.request.user, comment=comment)

    # -----------------------------------------------------------------
    def perform_update(self, serializer):
        reply = self.get_object()
        if reply.user != self.request.user:
            raise PermissionDenied("You can only edit your own replies.")
        serializer.save()
