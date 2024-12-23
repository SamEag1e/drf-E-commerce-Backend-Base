from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    head_line = models.TextField()
    text = models.TextField()
    image = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    writer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="writer"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="updated_by",
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Automatically generate slug from title if it doesn't exist
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
