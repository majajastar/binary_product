# order/models.py
from django.db import models
from myapps.users.models import User 
from myapps.prices.models import MinutePrice

def get_product_price_at_time(product_type, timestamp):
    """
    This function retrieves the product price at a specific timestamp.
    You should implement the logic based on how you track price history.
    """
    try:
        # Assuming you have a model that tracks price changes over time for each product
        # Here, I will assume you have a ProductPrice model with 'product', 'price', and 'timestamp'
        price_entry = MinutePrice.objects.filter(product_type=product_type, timestamp__lte=timestamp).order_by('-timestamp').first()
        
        if price_entry:
            return price_entry.price  # Return the price at the closest timestamp before or at the settlement time
        
    except ProductPrice.DoesNotExist:
        return None  # No price found at the given time

    return None  # Return None if no price is found

class Order(models.Model):
    ACTIVED = 'actived'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (ACTIVED, 'Actived'),
        (COMPLETED, 'Completed'),
    ]

    BUY_UP = 'buy_up'
    BUY_DOWN = 'buy_down'

    DIRECTION_CHOICES = [
        (BUY_UP, 'BuyUp'),
        (BUY_DOWN, 'BuyDown'),  # New status added here
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True)
    product = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()
    settled_price = models.FloatField(default=0)
    status =  models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVED)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default=BUY_UP)
    settled_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.product} for {self.user}"

    class Meta:
        ordering = ['-created_at']