"""serializers for proguide apis"""
from rest_framework import serializers

from core.models import ProGuide


class ProGuideSerializer(serializers.ModelSerializer):
    """serializer for proguide"""
    class Meta:
        model = ProGuide
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


class ProGuideDetailSerializer(ProGuideSerializer):
    """serializer for ProGuide detail view"""

    class Meta(ProGuideSerializer.Meta):
        fields = ProGuideSerializer.Meta.fields + ['description']
