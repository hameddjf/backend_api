"""
database models.
"""

from gettext import gettext as _
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


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
