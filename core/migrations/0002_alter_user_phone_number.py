# Generated by Django 4.2.3 on 2023-08-04 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.IntegerField(null=True),
        ),
    ]