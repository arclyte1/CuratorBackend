from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string
import logging

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        # Generate random password
        if not password:
            password_letters = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(random.choice(password_letters) for _ in range(128))
            logging.debug(f"GENERATED PASSWORD: {password}")

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions.py to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def set_name(self, name: str):
        self.name = ' '.join(name.split())
        self.save()


class Group(models.Model):
    title = models.CharField(max_length=255, blank=False)
    curators = models.ManyToManyField(User, related_name="groups", blank=True)


class Student(models.Model):
    name = models.CharField(max_length=255, blank=False)
    group = models.ForeignKey(Group, related_name='students', on_delete=models.CASCADE, blank=False)


class Event(models.Model):
    title = models.CharField(max_length=255, blank=False)
    type = models.CharField(max_length=255, default=None, blank=True, null=True)
    date = models.DateField(default=None, blank=True, null=True)
    start_time = models.TimeField(default=None, blank=True, null=True)
    end_time = models.TimeField(default=None, blank=True, null=True)
    location = models.CharField(max_length=255, default=None, blank=True, null=True)
    cloud_url = models.CharField(max_length=255, default=None, blank=True, null=True)
    groups = models.ManyToManyField(Group, related_name="events", blank=False)
    present_students = models.ManyToManyField(Student, related_name="present_events", blank=True)