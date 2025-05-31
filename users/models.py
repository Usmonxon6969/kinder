from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model with role-based permissions
    """
    ADMIN = 'admin'
    COOK = 'cook'
    MANAGER = 'manager'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (COOK, 'Chef'),
        (MANAGER, 'Manager'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=COOK)

    class Meta:
        ordering = ['username']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_cook(self):
        return self.role == self.COOK

    @property
    def is_manager(self):
        return self.role == self.MANAGER