from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    def get_full_path(self):
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Collection(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)


class ProductImage(models.Model):
    image = models.ImageField(upload_to="product_images/")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ManyToManyField(Category, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Inventory and SKU
    sku = models.CharField(max_length=100, unique=True)
    stock_quantity = models.IntegerField(default=0)

    # Pricing and discount
    original_price = models.BigIntegerField(validators=[MinValueValidator(0)])
    discount = models.IntegerField(
        default=0, validators=[MinValueValidator(0)]
    )
    discount_start_date = models.DateTimeField(blank=True, null=True)
    discount_end_date = models.DateTimeField(blank=True, null=True)

    # Product details
    description = models.TextField(blank=True)
    material = models.CharField(max_length=255, blank=True)
    weight = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
    )  # Weight in grams/carat
    size = models.CharField(max_length=100, blank=True, null=True)
    gemstone = models.CharField(max_length=255, blank=True, null=True)

    # Image
    image = models.ImageField(
        upload_to="product_images/", blank=True, null=True
    )
    additional_images = models.ManyToManyField(
        ProductImage, blank=True, related_name="additional_images"
    )

    # Tags and collections
    tags = models.ManyToManyField(Tag, blank=True)
    collection = models.ManyToManyField(
        Collection, related_name="products", blank=True
    )

    # Product visibility
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # SEO metadata
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    def __str__(self):
        return self.name
