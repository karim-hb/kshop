import string
import random

from django.contrib.admin.templatetags.admin_modify import prepopulated_fields_js
from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from django.contrib import admin
from datetime import timedelta
from .sender import send_otp
import uuid

from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=12)


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_foods = models.ForeignKey(
        'Foods', on_delete=models.SET_NULL, null=True, related_name='food')


class CollectionImage(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='core/images')


class Foods(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    unit_price = models.IntegerField()
    max_buy = models.IntegerField()
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)

    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)


class FoodImage(models.Model):
    food = models.ForeignKey(Foods, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='core/images')


class Customer(models.Model):
    gender = models.IntegerField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

    class Meta:
        ordering = ['user__first_name', 'user__last_name']


class Address(models.Model):
    street = models.CharField(max_length=255)
    plaque = models.FloatField()

    unit = models.FloatField()
    lat = models.FloatField()
    len = models.FloatField()
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="address")


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    description = models.TextField(null=True)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    food = models.ForeignKey(Foods, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.IntegerField()


class Cart(models.Model):
    # id = models.UUIDField(default=uuid4, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    foods = models.ForeignKey(Foods, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [['cart', 'foods']]


class Review(models.Model):
    foods = models.ForeignKey(Foods, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    # score = models.IntegerField()


class OtpRequestQuerySet(models.QuerySet):
    def is_valid(self, receiver, request, password):
        current_time = timezone.now()
        return self.filter(
            receiver=receiver,
            request_id=request,
            password=password,
            created__lt=current_time,
            created__gt=current_time - timedelta(seconds=120),

        ).exists()


class OTPManager(models.Manager):

    def get_queryset(self):
        return OtpRequestQuerySet(self.model, self._db)

    def is_valid(self, receiver, request, password):
        return self.get_queryset().is_valid(receiver, request, password)

    def generate(self, data):
        otp = self.model(channel=data['channel'], receiver=data['receiver'])
        otp.save(using=self._db)
        send_otp(otp)
        return otp


def generate_otp():
    rand = random.SystemRandom()
    digits = rand.choices(string.digits, k=4)
    return ''.join(digits)


class OtpRequest(models.Model):
    class OtpChannel(models.TextChoices):
        PHONE = 'Phone'
        EMAIL = 'E-Mail'

    request_id = models.AutoField(primary_key=True)
    channel = models.CharField(max_length=10, choices=OtpChannel.choices, default=OtpChannel.PHONE)
    receiver = models.CharField(max_length=50)
    password = models.CharField(max_length=4, default=generate_otp)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    objects = OTPManager()
