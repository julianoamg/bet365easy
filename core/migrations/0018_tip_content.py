# Generated by Django 4.1.7 on 2023-03-15 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_tip_create_bet'),
    ]

    operations = [
        migrations.AddField(
            model_name='tip',
            name='content',
            field=models.TextField(null=True),
        ),
    ]
