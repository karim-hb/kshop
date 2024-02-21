# Generated by Django 4.2.3 on 2023-08-26 01:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_alter_user_phone_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="address",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.address",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="description",
            field=models.TextField(null=True),
        ),
    ]