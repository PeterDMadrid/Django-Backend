# Generated by Django 5.1.3 on 2025-01-31 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_customuser_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='signing',
            field=models.IntegerField(default=0),
        ),
    ]
