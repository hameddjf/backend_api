"""url mappings for the proguide app"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from proguide.views import ProGuideViewSet

router = DefaultRouter()
router.register('proguides', ProGuideViewSet)

app_name = 'proguide'

urlpatterns = [
    path('', include(router.urls)),

]
