from . import views
from django.urls import path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register('connreq',views.ConnectionRequestViewSet,basename='connreq')
router.register('connection',views.ConnectionsViewSet,basename='connection')
router.register('likes',views.LikesViewSet,basename='likes')
urlpatterns = router.urls