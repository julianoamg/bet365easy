# Generated by Django 4.1.7 on 2023-04-18 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_remove_bot_send_image_remove_bot_send_text_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bot',
            name='unit_text',
            field=models.CharField(default='Unidades', max_length=100, verbose_name='Texto das unidades:'),
        ),
    ]
