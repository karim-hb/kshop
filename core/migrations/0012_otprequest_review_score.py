# Generated by Django 4.2.3 on 2023-08-21 01:14

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_alter_address_customer"),
    ]

    operations = [
        migrations.CreateModel(
            name="OtpRequest",
            fields=[
                ("request_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "channel",
                    models.CharField(
                        choices=[("Phone", "Phone"), ("E-Mail", "Email")],
                        default="Phone",
                        max_length=10,
                    ),
                ),
                ("receiver", models.CharField(max_length=50)),
                (
                    "password",
                    models.CharField(default=core.models.generate_otp, max_length=4),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name="review",
            name="score",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]