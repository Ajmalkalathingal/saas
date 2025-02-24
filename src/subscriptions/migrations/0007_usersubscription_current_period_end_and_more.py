# Generated by Django 5.0.10 on 2025-02-24 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0006_usersubscription_user_cancelled'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='current_period_end',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usersubscription',
            name='current_period_start',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usersubscription',
            name='original_period_start',
            field=models.DateField(blank=True, null=True),
        ),
    ]
