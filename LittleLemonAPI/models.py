from django.db import models


# Create your models here.

class Category(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.title} || {self.menu_items.count()}"


class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    inventory = models.IntegerField()
    # we used on_delete=models.PROTECT to prevent deleting the category if it has a menu item
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='menu_items', default=1)

    def __str__(self):
        return self.title
