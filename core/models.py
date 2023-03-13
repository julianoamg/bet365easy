from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from model_utils.models import UUIDModel, TimeStampedModel
from django.db import models


class Plan(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name='Nome')
    period_in_days = models.IntegerField(default=0, verbose_name='Período em dias')

    def __str__(self):
        return f'{self.name} - {self.period_in_days} dias'

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
    name = models.CharField(null=True, max_length=255, verbose_name='Nome')
    telegram = models.CharField(null=True, max_length=100, verbose_name='Telegram')
    whatsapp = models.CharField(null=True, blank=True, max_length=100, verbose_name='WhatsApp')
    plan = models.ForeignKey(Plan, null=True, on_delete=models.CASCADE, verbose_name='Plano')
    payment_date = models.DateField(null=True, verbose_name='Data de Pagamento')
    price = models.DecimalField(max_digits=20, default=0, decimal_places=2, verbose_name='Valor da Mensalidade')
    email = models.EmailField(max_length=255, unique=True, verbose_name='E-mail')
    is_staff = models.BooleanField(default=False, verbose_name='É da equipe')
    is_superuser = models.BooleanField(default=False, verbose_name='É super usuário?')
    is_active = models.BooleanField(default=True, verbose_name='Está ativo?')

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    @property
    def expire_in_days(self):
        if self.is_superuser:
            return 1000
        if not self.plan:
            return 0
        expire_date = self.payment_date + timedelta(days=self.plan.period_in_days)
        return (expire_date - timezone.localtime().date()).days

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'


class Bot(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Cliente')
    token = models.CharField(max_length=255, verbose_name='BotFather Token')
    dialog_id = models.BigIntegerField(verbose_name='ID do Grupo/Canal')
    dialog_name = models.CharField(max_length=255, verbose_name='Nome do Grupo/Canal')
    members_qty = models.IntegerField(default=0, editable=False, verbose_name='Quantidade de membros')

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
    class House(models.TextChoices):
        BET365 = 'BET365', 'BET365'
        BETANO = 'BETANO', 'BETANO'

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Cliente')
    bot = models.ForeignKey(Bot, null=True, on_delete=models.CASCADE, verbose_name='Bot')
    title = models.CharField(max_length=255, verbose_name='Título')
    odd = models.CharField(max_length=255, verbose_name='Odd')
    market = models.CharField(max_length=255, verbose_name='Mercado')
    game = models.CharField(max_length=255, verbose_name='Jogo')
    bet = models.CharField(null=True, max_length=1000, verbose_name='Caderneta BET365')
    sent = models.BooleanField(default=False, verbose_name='Enviado?')
    units = models.FloatField(default=1, verbose_name='Unidades')
    link = models.URLField(null=True, verbose_name='Link')
    house = models.CharField(null=True, max_length=100, choices=House.choices, verbose_name='House')
    sum_odds = models.FloatField(null=True, verbose_name='Soma Odds')

    class Meta:
        verbose_name = 'Tip'
        verbose_name_plural = 'Tips'
