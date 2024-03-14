"""
serializers for the user api view.
"""
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5
            }
        }

    # just return when the status code is 201 (is successful)
    def create(self, validated_data):
        """create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """updated and return user"""
        # retrieve the password from validated_data then remove password(pop)
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """serializer for the user auth token."""
    email = serializers.EmailField()

    # تعیین نوع ورودی از نوع پسورد
    # اگه یوزر در پسوردش فضای خالی بزاره اون در سیستم حفظ بشه ک پیشفرض حذف میشه
    password = serializers.CharField(
        style={
            'input_type': 'password',
        },
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            message = _("نمیتوان احراز هویت انجام داد.")
            raise serializers.ValidationError(message, code='authorization')
        attrs['user'] = user
        return attrs
