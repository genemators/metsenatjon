from django.contrib.auth.base_user import BaseUserManager
from django.db.models.manager import Manager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def _create_user(self, phone, password, **extra_fields):
        """
        Create and save a user with the given phone, and password.
        """
        if not phone:
            raise ValueError(_("Phone number is required"))

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self._create_user(phone, password, **extra_fields)


class ModelManager(Manager):
    def active(self):
        return self.get_queryset().filter(active=True)