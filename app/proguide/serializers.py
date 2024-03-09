"""serializers for proguide apis"""
from rest_framework import serializers

from core.models import ProGuide, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """serializer for tags"""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """serializer for ingredients"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProGuideSerializer(serializers.ModelSerializer):
    """serializer for proguide"""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = ProGuide
        fields = ['id', 'title', 'time_minutes',
                  'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id']

    # در ابتدای نام تابع اندرسکور ب معنای تاکید هستش
    def _get_or_create_tags(self, tags, proguide):
        """handle getting or creating tags as needed"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                # getting all value asign to tags
                **tag,
            )
            proguide.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, proguide):
        """handle getting or creating ingredients as needed"""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, create = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            proguide.ingredients.add(ingredient_obj)

    def create(self, validated_date):
        """create a proguide """
        # using pop for ensore remove tags befor create (getting empty list)
        tags = validated_date.pop('tags', [])
        ingredients = validated_date.pop('ingredients', [])
        proguide = ProGuide.objects.create(**validated_date)
        self._get_or_create_tags(tags, proguide)
        self._get_or_create_ingredients(ingredients, proguide)

        return proguide

    def update(self, instance, validated_data):
        """updating proguide"""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ProGuideDetailSerializer(ProGuideSerializer):
    """serializer for ProGuide detail view"""

    class Meta(ProGuideSerializer.Meta):
        fields = ProGuideSerializer.Meta.fields + ['description', 'image']


class ProGuideImageSerializer(serializers.ModelSerializer):
    """serializer for uploading images to proguide"""
    class Meta:
        model = ProGuide
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
