# Generated by Django 5.0.10 on 2025-02-24 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0008_alter_usersubscription_current_period_end_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersubscription',
            name='original_period_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
