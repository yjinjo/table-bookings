# Generated by Django 4.2 on 2023-05-01 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="profile_image",
            field=models.ImageField(null=True, upload_to="uploads/%Y/%m/%d/"),
        ),
    ]