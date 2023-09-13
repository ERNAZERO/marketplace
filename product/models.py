from django.db import models
from user.models import Seller, Customer


class Category(models.Model):
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    price = models.IntegerField(null=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.PositiveIntegerField(default=0)
    total_rating_points = models.PositiveIntegerField(default=0)
    views_by = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class ProductRating(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='ratings', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()

    class Meta:
        unique_together = ('product', 'customer')


class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product)

    def __str__(self):
        return f'{self.customer.email}`s cart'


class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)



