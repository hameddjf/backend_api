"""views for the proguide apis"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import ProGuide, Tag, Ingredient
from proguide.serializers import (
    ProGuideSerializer,
    ProGuideDetailSerializer,
    TagSerializer,
    IngredientSerializer,
)


class ProGuideViewSet(viewsets.ModelViewSet):
    """view for manage proguide apis"""
    serializer_class = ProGuideDetailSerializer
    queryset = ProGuide.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """retrieve proguide for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """return the serializer class for request"""

        if self.action == 'list':
            return ProGuideSerializer
        return self.serializer_class

    # This method assumes that data has already been validated by serializer
    def perform_create(self, serializer):
        """Saves a new proguide linked to the current user."""
        serializer.save(user=self.request.user)


class TagViewSet(
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """manage tags in the database"""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """filter queryset to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class IngredientViewSet(mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """manage ingredients in the database"""
    # set the ingredientserializer to serializer_classes
    serializer_class = IngredientSerializer
    # set all oobjects of ingredient model to queryset
    queryset = Ingredient.objects.all()
    # set authentication token to authentication_classes
    authentication_classes = [TokenAuthentication]
    # for using this endpoint user must be authenticated
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """filter queryset to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
