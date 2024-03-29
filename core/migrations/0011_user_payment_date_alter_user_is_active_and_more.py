# Generated by Django 4.1.7 on 2023-03-10 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_user_name_user_telegram_user_whatsapp'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='payment_date',
            field=models.DateField(blank=True, null=True, verbose_name='Data de Pagamento'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Está ativo?'),
        ),
        migrations.AlterField(
            model_name='user',
            name='telegram',
            field=models.CharField(max_length=100, null=True, verbose_name='Telegram'),
        ),
        migrations.AlterField(
            model_name='user',
            name='whatsapp',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='WhatsApp'),
        ),
    ]
