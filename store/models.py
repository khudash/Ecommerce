from django.db import models


class Hero(models.Model):
    heading = models.CharField(max_length=200)
    heading_green = models.CharField(max_length=200)
    sub_heading = models.TextField()
    button_text = models.CharField(max_length=100)
    button_link = models.CharField(max_length=200, default="#")
    image = models.ImageField(upload_to="hero/")

    def __str__(self):
        return self.heading
    
# ==================

class Benefit(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(
        max_length=100,
        help_text="Example: droplet, roots, nourishment, star"
    )

    def __str__(self):
        return self.title


class FormulaSection(models.Model):
    sub_title = models.CharField(max_length=200, default="NATURAL FORMULA")
    title = models.CharField(max_length=200, default="Powered By Nature")
    description = models.TextField(default="Carefully selected natural ingredients come together to create a nourishing hair-care formula.")
    center_image = models.ImageField(upload_to="formula/", help_text="Upload middle image for Natural Formula section")

    def __str__(self):
        return self.title


# ///////////////////////

class Product(models.Model):
    name = models.CharField(max_length=200)
    size = models.CharField(max_length=50, default="50ml", help_text="e.g. 50ml, 80ml, 120ml")
    subtitle = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. 50ml Trial & Travel Edition")
    badge = models.CharField(max_length=100, blank=True, null=True, default="Starter Pack", help_text="e.g. Starter Pack, Most Popular, Best Value")
    is_featured = models.BooleanField(default=False, help_text="Highlight card with featured border & badge")

    image = models.ImageField(
        upload_to="products/"
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Current / New Price"
    )

    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Previous / Old Price"
    )

    discount = models.PositiveIntegerField(
        default=0,
        help_text="Discount percentage e.g. 25, 30"
    )

    delivery_text = models.CharField(
        max_length=255,
        default="Free delivery on orders above Rs. 2,500"
    )

    is_available = models.BooleanField(
        default=True
    )

    @property
    def savings(self):
        if self.old_price and self.old_price > self.price:
            return self.old_price - self.price
        return 0

    def __str__(self):
        return f"{self.name} ({self.size})"


# ================== ORDER & CHECKOUT MODELS ==================

class Order(models.Model):
    PAYMENT_CHOICES = (
        ('easypaisa', 'Easypaisa'),
        ('jazzcash', 'JazzCash'),
        ('meezan', 'Meezan Bank'),
        ('hbl', 'HBL Bank'),
        ('cod', 'Cash on Delivery'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='cod')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} (Order #{self.order.id})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=250, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


# ================== REVIEWS & TESTIMONIALS MODELS ==================

class ReviewSectionSettings(models.Model):
    badge_text = models.CharField(max_length=100, default="Customer Love", help_text="Small top badge text")
    heading = models.CharField(max_length=200, default="Loved By Hair", help_text="Main heading before highlight")
    heading_green = models.CharField(max_length=200, default="Care Lovers", help_text="Highlighted green part of heading")
    sub_heading = models.TextField(default="See what our customers have to say about their hair-care experience.", help_text="Subtitle under heading")
    rating_score = models.DecimalField(max_digits=3, decimal_places=1, default=4.9, help_text="Overall displayed rating (e.g. 4.9)")
    total_reviews_text = models.CharField(max_length=100, default="Based on 128 reviews", help_text="e.g. Based on 128 reviews, 500+ Happy Customers")
    verified_label = models.CharField(max_length=100, default="Verified customer reviews", help_text="Verified label text")

    class Meta:
        verbose_name = "Reviews Section Setting"
        verbose_name_plural = "Reviews Section Settings"

    def __str__(self):
        return f"Review Section ({self.rating_score}★ - {self.total_reviews_text})"


class Review(models.Model):
    name = models.CharField(max_length=150, help_text="Customer full name e.g. Sarah Ahmed")
    rating = models.PositiveSmallIntegerField(
        default=5,
        choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')],
        help_text="Rating out of 5 stars"
    )
    comment = models.TextField(help_text="Customer review feedback text")
    verified_badge = models.CharField(max_length=100, default="Verified Customer", help_text="e.g. Verified Customer, Verified Buyer")
    city = models.CharField(max_length=100, blank=True, null=True, help_text="Optional city e.g. Lahore, Karachi, Islamabad")
    image = models.ImageField(upload_to="reviews/", blank=True, null=True, help_text="Optional customer avatar/photo")
    is_approved = models.BooleanField(default=True, help_text="Check to display on the website")
    is_featured = models.BooleanField(default=False, help_text="Pin to the front")
    order = models.PositiveIntegerField(default=0, help_text="Display order (0 shows first)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    @property
    def initials(self):
        parts = self.name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        elif parts and len(parts[0]) >= 2:
            return parts[0][:2].upper()
        elif parts:
            return parts[0][0].upper()
        return "VC"

    @property
    def stars_list(self):
        return range(min(max(int(self.rating), 1), 5))

    @property
    def empty_stars_list(self):
        return range(5 - min(max(int(self.rating), 1), 5))

    def __str__(self):
        return f"{self.name} ({self.rating}★) - {self.comment[:30]}"