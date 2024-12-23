from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ("active", "Active"),
        ("ordered", "Ordered"),
        ("delivered", "Delivered"),
    ]
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ordered_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    def calculate_total_price(self, price_per_gram):
        return sum(
            item.calculate_total_price(price_per_gram)
            for item in self.cart_items.all()
        )

    def __str__(self):
        return f"Cart for {self.user.username} (Status: {self.status})"


class CartItem(models.Model):
    cart = models.ForeignKey(
        ShoppingCart, related_name="cart_items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def total_weight(self):
        return self.product.weight * self.quantity

    def calculate_total_price(self, price_per_gram):
        return self.total_weight() * price_per_gram

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}, {self.total_weight()}g total)"
