from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from model_utils.models import UUIDModel, TimeStampedModel
from django.db import models


class Plan(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name='Nome')
    period_in_days = models.IntegerField(default=0, verbose_name='Período em dias')

    class Meta:
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(UUIDModel, TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    plan = models.ForeignKey(Plan, null=True, on_delete=models.CASCADE, verbose_name='Plano')
    email = models.EmailField(max_length=255, unique=True, verbose_name='E-mail')
    is_staff = models.BooleanField(default=False, verbose_name='É da equipe')
    is_superuser = models.BooleanField(default=False, verbose_name='É super usuário?')
    is_active = models.BooleanField(default=False, verbose_name='Está ativo?')

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'


class Bot(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Cliente')
    token = models.CharField(max_length=255, verbose_name='BotFather Token')
    dialog_id = models.IntegerField(verbose_name='ID do Grupo/Canal')
    dialog_name = models.CharField(max_length=255, verbose_name='Nome do Grupo/Canal')

    def __str__(self):
        return self.dialog_name

    class Meta:
        verbose_name = 'Bot'
        verbose_name_plural = 'Bots'


class Session(UUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Sessão'
        verbose_name_plural = 'Sessões'


class Tip(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Cliente')
    bot = models.ForeignKey(Bot, null=True, on_delete=models.CASCADE, verbose_name='Bot')
    title = models.CharField(max_length=255, verbose_name='Título')
    odd = models.CharField(max_length=255, verbose_name='Odd')
    market = models.CharField(max_length=255, verbose_name='Mercado')
    game = models.CharField(max_length=255, verbose_name='Jogo')
    bet = models.CharField(max_length=255, verbose_name='Caderneta BET365')
    sent = models.BooleanField(default=False, verbose_name='Enviado?')

    class Meta:
        verbose_name = 'Tip'
        verbose_name_plural = 'Tips'
