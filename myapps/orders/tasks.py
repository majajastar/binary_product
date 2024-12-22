# orders/tasks.py
from celery import shared_task
from myapps.orders.models import Order
from django.utils import timezone
from datetime import timedelta
from myapps.prices.models import MinutePrice
import logging
# Get a logger instance
logger = logging.getLogger(__name__)

def get_product_price_at_time(product_type, timestamp):
    try:
        print(product_type, timestamp)
        price_entry = MinutePrice.objects.filter(product_type=product_type, timestamp__lte=timestamp).order_by('-timestamp').first()
        
        if price_entry:
            return price_entry.close  # Return the price at the closest timestamp before or at the settlement time
        
    except ProductPrice.DoesNotExist:
        return None  # No price found at the given time

    return None  # Return None if no price is found

@shared_task
def check_and_settle_orders():
    """
    This task checks all orders and settles those that meet the criteria.
    It should be run every 5 minutes.
    """
    # Get all pending orders
    pending_orders = Order.objects.filter(status=Order.ACTIVED)
    datetime_now = timezone.now()
    # Example: Settle orders if the deadline has passed
    for order in pending_orders:
        # Here, implement your criteria for settling the orders.
        # For example, if it's past the deadline, mark as settled:
        product_price_at_settlement = get_product_price_at_time(order.product, order.settled_at)
        if (not product_price_at_settlement):
            order.settled_price = order.price
        else:
            order.settled_price = product_price_at_settlement
        user = order.user
        if order.direction == order.BUY_UP:
            user.funds += order.settled_price
        else:
            user.funds -= order.settled_price
        order.status = Order.COMPLETED  # Set to settle
        order.save()

    return "Orders checked and settled"


@shared_task
def debug_task():
    datetime_now = timezone.now()
    logger.info(datatime_now)
    return "test"