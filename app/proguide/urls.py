"""url mappings for the proguide app"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from proguide.views import (ProGuideViewSet, TagViewSet, IngredientViewSet)

router = DefaultRouter()
router.register('proguides', ProGuideViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

app_name = 'proguide'

urlpatterns = [
    path('', include(router.urls)),

]
