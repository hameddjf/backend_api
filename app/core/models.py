"""
database models.
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
from django.utils.translation import gettext_lazy as _

import uuid
import os


def proguide_image_file_path(instance, filename):
    """generate file path for new proguide image"""
    # Extract filename
    extention = os.path.splitext(filename)[1]
    # create filename by create uuid & extention
    filename = f'{uuid.uuid4()}{extention}'

    return os.path.join('uploads', 'proguide', filename)


class UserManager(BaseUserManager):
    "manager for users."

    def create_user(self, email, password=None, **extra_fields):
        """create, save and return a new user."""
        if not email:
            raise ValueError('کاربر باید دارای یک حساب ایمیل باشد.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """user in the system."""
    email = models.EmailField(_("ایمیل"), max_length=254, unique=True)
    name = models.CharField(_("اسم"), max_length=50)
    is_active = models.BooleanField(_("فعال است؟"), default=True)
    is_staff = models.BooleanField(_("کارمند است؟"), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class ProGuide(models.Model):
    """ProGuide objects"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_("کاربر"),
                             on_delete=models.CASCADE)
    title = models.CharField(_("عنوان"), max_length=500)
    description = models.TextField(_("توضیحات"), blank=True)
    time_minutes = models.IntegerField(_("زمان بر دقیقه"))
    price = models.DecimalField(_("قیمت"), max_digits=9, decimal_places=2)
    link = models.CharField(_("لینک"), max_length=500, blank=True)

    tags = models.ManyToManyField("Tag", verbose_name=_("تگ"))
    ingredients = models.ManyToManyField("Ingredient", verbose_name=_("تگ"))
    image = models.ImageField(_("تصویر"), upload_to=proguide_image_file_path,
                              height_field=None, width_field=None,
                              max_length=None, null=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """tag for filtering ProGuide"""
    name = models.CharField(_("اسم"), max_length=503)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_("کاربر"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("تگ")
        verbose_name_plural = _("تگها")

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ingredient for ProGuide"""
    name = models.CharField(_("نام"), max_length=500)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_("کاربر"), on_delete=models.CASCADE)

    def __str__(self):
        return self.name
