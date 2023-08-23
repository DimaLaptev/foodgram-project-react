from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):

    class Roles(models.TextChoices):
        USER = 'user'
        ADMIN = 'admin'

    username = models.CharField(
        verbose_name='username',
        max_length=150,
        unique=True,
        validators=(RegexValidator(
            regex=r'^[\w.@+-]+\Z', message=(
                'Incorrect value "username" entered')
        ),)
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=254,
        db_index=True,
        unique=True,
        help_text='Enter your email address',
    )
    first_name = models.CharField(
        verbose_name='name',
        max_length=150,
        help_text='Enter the name',
    )
    last_name = models.CharField(
        verbose_name='Last name',
        max_length=150,
        help_text='Enter the last name',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'users'
        ordering = ('id',)

    @property
    def is_admin(self):
        return (self.is_staff or self.is_superuser
                or self.role == User.Roles.ADMIN)

    @property
    def is_user(self):
        return self.is_user or self.role == User.Roles.USER

    def __str__(self):
        return f'@{self.username}: {self.email}.'


class Subscribe(models.Model):
    '''Subscriber-model'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='subscriber',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Author',
    )
    created = models.DateTimeField(
        'Date of subscribe',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribing',
            ),
        )

    def __str__(self):
        return (f'User {self.user.username} '
                f'subscribe of {self.author.username}')
