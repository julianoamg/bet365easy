# Generated by Django 4.1.7 on 2023-03-13 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_tip_sum_odds'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tip',
            name='bet',
            field=models.CharField(max_length=1000, null=True, verbose_name='Caderneta BET365'),
        ),
    ]
