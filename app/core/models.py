from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,\
                                        PermissionsMixin


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        "creaets and saves anew user with email"
        if not email:
            raise ValueError("A User must Have an Email")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    "Base Class For User Model that users can use thier email"
    email = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
