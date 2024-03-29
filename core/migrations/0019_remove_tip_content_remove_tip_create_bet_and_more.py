# Generated by Django 4.1.7 on 2023-03-20 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_tip_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tip',
            name='content',
        ),
        migrations.RemoveField(
            model_name='tip',
            name='create_bet',
        ),
        migrations.RemoveField(
            model_name='tip',
            name='game',
        ),
        migrations.RemoveField(
            model_name='tip',
            name='market',
        ),
        migrations.RemoveField(
            model_name='tip',
            name='odd',
        ),
        migrations.RemoveField(
            model_name='tip',
            name='sent',
        ),
        migrations.RemoveField(
            model_name='tip',
            name='sum_odds',
        ),
        migrations.RemoveField(
            model_name='tip',
            name='title',
        ),
        migrations.AddField(
            model_name='tip',
            name='print',
            field=models.TextField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='tip',
            name='source',
            field=models.TextField(editable=False, null=True),
        ),
    ]
