# Generated by Django 5.2 on 2025-06-14 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_baseshopitem_rarity'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseshopitem',
            name='is_donation_only',
            field=models.BooleanField(default=False),
        ),
    ]
