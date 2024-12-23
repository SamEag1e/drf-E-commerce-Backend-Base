from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, ReplyViewSet

router = DefaultRouter()
router.register(r"", CommentViewSet, basename="comment")
router.register(r"replies", ReplyViewSet, basename="reply")

urlpatterns = router.urls
