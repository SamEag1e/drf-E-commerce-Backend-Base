from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()


# ---------------------------------------------------------------------
class RestrictedWord(models.Model):
    word = models.CharField(max_length=50, unique=True)

    # -----------------------------------------------------------------
    def __str__(self):
        return self.word


# ---------------------------------------------------------------------
class Censorable(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_visible = models.BooleanField(default=True)

    # -----------------------------------------------------------------
    class Meta:
        # This class is just for inheritance,
        # It won't create a table.
        abstract = True


# ---------------------------------------------------------------------
class Comment(Censorable):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # -----------------------------------------------------------------
    def __str__(self):
        return (
            f"Comment by {str(self.user)} on "
            f"{self.content_object} ({self.content[:20]})"
        )


# ---------------------------------------------------------------------
class Reply(Censorable):
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="replies"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="replies"
    )

    # -----------------------------------------------------------------
    def __str__(self):
        return f"Reply by {str(self.user)} to comment {self.comment.id}"
