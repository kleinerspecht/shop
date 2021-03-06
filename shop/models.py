from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from django.urls import reverse

from ecommerce_shop import settings


# Create your models here.
from django_countries.fields import CountryField

DELIVEY_CHOICES = [
    ('Order confirmed!', 'Order confirmed!'),
    ('Order processed!', 'Order processed!'),
    ('Order dispatched!', 'Order dispatched!'),
    ('Order arrived!', 'Order arrived!')

]

class CreateUser(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder':('Username'), 'size':36})
        self.fields['email'].widget.attrs.update({'placeholder':('Email'), 'size':36})
        self.fields['password1'].widget.attrs.update({'placeholder':('Password'), 'size':36})
        self.fields['password2'].widget.attrs.update({'placeholder':('Repeat password'), 'size':36})

class Categories(models.Model):
    cat_name = models.CharField(max_length=100, null=True, blank=True)
    cat_info = models.CharField(max_length=100, null=True, blank=True)

    @property
    def cat_product_num(self):
        model = Item.objects.filter(item_category=self.cat_name)
        return model.objects.count()

    def __str__(self):
        return self.cat_name

class Item(models.Model):
    item_price = models.FloatField(null=True, blank=True)
    item_info = models.CharField(max_length=150, null=True, blank=True)
    item_category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True, blank=True)
    item_image = models.ImageField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)

    @property
    def on_stock(self):
        return [qty for qty in range(self.stock)]

class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    
    @property
    def item_pricing(self):
        return f'{self.item.item_price * self.quantity:.2f}'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField()
    confirmed = models.BooleanField(default=False)
    billing_address = models.ForeignKey("PaymentModel", on_delete=models.SET_NULL, blank=True, null=True, related_name='billing_address')
    payment = models.ForeignKey("PaidOrders", on_delete=models.SET_NULL, blank=True, null=True, related_name='payment')
    delivery_status = models.CharField(max_length=70, choices=DELIVEY_CHOICES, null=True, blank=True,)

    @property
    def total_price(self):
        total = 0
        for item in self.items.all():
            total += float(item.item_pricing)
        return f'{total:.2f}'

    @property
    def tax_total_price(self):
        total = 0
        tax = 2
        for item in self.items.all():
            total += float(item.item_pricing) + tax
        return f'{total:.2f}'

class PaymentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=200)
    street_address_2 = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200)
    zip = models.CharField(max_length=100)


class PaidOrders(models.Model):
    stripe_charge_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount =  models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)











