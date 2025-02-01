# Generated by Django 5.1.3 on 2025-02-01 03:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_score_user_alter_customuser_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='score',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_score_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
