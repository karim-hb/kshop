# Generated by Django 4.2.3 on 2023-08-21 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_remove_review_score"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(default=1, max_length=12),
            preserve_default=False,
        ),
    ]
