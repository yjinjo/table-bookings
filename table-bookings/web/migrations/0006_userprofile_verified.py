# Generated by Django 4.2 on 2023-05-01 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0005_alter_userverification_verified_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="verified",
            field=models.BooleanField(default=False),
        ),
    ]