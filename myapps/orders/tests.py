# order/models.py
from django.db import models
from users.models import User  # Assuming User model exists in the users app

class Order(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')  # ForeignKey to User
    product = models.CharField(max_length=100)  # Example product field
    quantity = models.PositiveIntegerField()  # Quantity of the product
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the order
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the order was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the order was last updated

    def __str__(self):
        return f"Order #{self.id} - {self.product} for {self.user}"

    class Meta:
        ordering = ['-created_at']
