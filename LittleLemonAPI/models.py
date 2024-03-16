from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Category(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.title} || {self.menu_items.count()}"


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(default=False, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='menu_items')

    def __str__(self):
        return f"{self.id} {self.title}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_items = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('user', 'menu_items')

    def __str__(self):
        return f"{self.user.username}'s cart"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='delivery_crew', null=True)
    status = models.BooleanField(default=0, db_index=True)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.user.username}'s order"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order', 'menu_item')

    def __str__(self):
        return f"{self.order.user.username}'s order item"
