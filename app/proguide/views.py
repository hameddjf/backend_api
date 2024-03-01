"""views for the proguide apis"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import ProGuide
from proguide.serializers import ProGuideSerializer, ProGuideDetailSerializer


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
