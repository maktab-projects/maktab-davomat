from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    DIRECTOR = 'director'
    ADMIN = 'admin'
    TEACHER = 'teacher'

    ROLE_CHOICES = [
        (DIRECTOR, 'Director'),
        (ADMIN, 'Admin'),
        (TEACHER, 'Teacher'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=TEACHER)
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=100, blank=True)

    @property
    def full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.username

    def __str__(self):
        return f"{self.username} ({self.role})"
