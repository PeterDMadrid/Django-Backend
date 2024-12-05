# Generated by Django 5.1.3 on 2024-12-05 15:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_score_customuser_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='score',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to='accounts.score'),
        ),
    ]
