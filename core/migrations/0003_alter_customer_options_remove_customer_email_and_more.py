# Generated by Django 4.2.3 on 2023-08-05 18:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_user_phone_number"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="customer",
            options={"ordering": ["user__first_name", "user__last_name"]},
        ),
        migrations.RemoveField(
            model_name="customer",
            name="email",
        ),
        migrations.RemoveField(
            model_name="customer",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="customer",
            name="last_name",
        ),
        migrations.RemoveField(
            model_name="customer",
            name="phone",
        ),
        migrations.AddField(
            model_name="customer",
            name="gender",
            field=models.IntegerField(default=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="customer",
            name="user",
            field=models.OneToOneField(
                default=2,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="items",
                to="core.order",
            ),
        ),
    ]
