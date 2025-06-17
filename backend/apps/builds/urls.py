from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BuildTaskViewSet, BuildHistoryViewSet

router = DefaultRouter()
router.register('tasks', BuildTaskViewSet)
router.register('history', BuildHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 