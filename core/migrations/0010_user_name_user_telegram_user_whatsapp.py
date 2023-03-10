# Generated by Django 4.1.7 on 2023-03-10 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_bot_dialog_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=255, null=True, verbose_name='Nome Completo'),
        ),
        migrations.AddField(
            model_name='user',
            name='telegram',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Telegram'),
        ),
        migrations.AddField(
            model_name='user',
            name='whatsapp',
            field=models.CharField(max_length=100, null=True, verbose_name='WhatsApp'),
        ),
    ]
