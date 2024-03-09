"""views for the proguide apis"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import ProGuide, Tag, Ingredient
from proguide.serializers import (
    ProGuideSerializer,
    ProGuideDetailSerializer,
    TagSerializer,
    IngredientSerializer,
    ProGuideImageSerializer,
)


# DRF در ویوهای  OpenAPI دکوریتوری برای افزودن یا تغییر مستندات
@extend_schema_view(
    list=extend_schema(
        parameters=[
            # جدا شده توسط ویرگول ID هایبرای فیلتر کردن با 'tags' تعریف پارامتر
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='فهرست شناسه‌ها برای فیلتر کردن با , جدا شده'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='لیستی از شناسه‌های عناصر برا فیلتر با , جدا شده'
            )
        ]
    )
)
class ProGuideViewSet(viewsets.ModelViewSet):
    """view for manage proguide apis"""
    serializer_class = ProGuideDetailSerializer
    queryset = ProGuide.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """convert a list of strings to integers(like:'1,2,3')"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """retrieve proguide for authenticated user"""
        # تبدیل پارامترهای دریافتی از کوئری استرینگ به صحیح (مانند: '1,2,3')
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            """
            QuerySet به اعداد صحیح و فیلتر کردن  tags تبدیل مقادیر
            بر اساس شناسه‌های tags"""
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            """
            QuerySet به اعداد صحیح و فیلتر کردن  ingredients تبدیل مقادیر
            بر اساس شناسه‌های ingredients"""
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        # برای بازگرداندن موارد مرتبط با کاربر جاری، QuerySet فیلتر کننده نهایی
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        """return the serializer class for request"""

        if self.action == 'list':
            return ProGuideSerializer
        elif self.action == 'upload_image':
            return ProGuideImageSerializer

        return self.serializer_class

    # This method assumes that data has already been validated by serializer
    def perform_create(self, serializer):
        """Saves a new proguide linked to the current user."""
        serializer.save(user=self.request.user)

    """
    defines a custom action 'upload-image' for POST requests
    on a single resource in a ViewSet(specific id in proguide)"""
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """upload an image to proguide"""
        proguide = self.get_object()
        serializer = self.get_serializer(proguide, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


# Filter items by proguide assignment.
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='filter by items assigned to proguides',
            )
        ]
    )
)
class BaseProGuideAttrViewSet(mixins.DestroyModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    """manage tags in the database"""
    # set authentication token to authentication_classes
    authentication_classes = [TokenAuthentication]
    # for using this endpoint user must be authenticated
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """filter queryset to authenticated user"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(proguide__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


class TagViewSet(BaseProGuideAttrViewSet):
    """manage tags in the database"""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseProGuideAttrViewSet):
    """manage ingredients in the database"""
    # set the ingredientserializer to serializer_classes
    serializer_class = IngredientSerializer
    # set all oobjects of ingredient model to queryset
    queryset = Ingredient.objects.all()
