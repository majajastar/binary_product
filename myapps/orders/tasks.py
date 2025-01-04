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
    settled_count = 0

    for order in pending_orders:
        # Retrieve the product price at settlement time
        product_price_at_settlement = get_product_price_at_time(order.product, order.settled_at)

        if not product_price_at_settlement:
            order.settled_price = order.price
        else:
            order.settled_price = product_price_at_settlement

        user = order.user
        quantity = order.quantity
        if order.direction == order.BUY_UP:
            user.funds += order.settled_price * quantity
        else:
            user.buy_down_limit += order.price * quantity
            user.funds -= order.settled_price * quantity
        order.status = Order.COMPLETED  # Mark order as completed
        order.save()
        user.save()
        # Log info about the completed order
        logger.info(
            f"Order ID {order.id} settled:\n"
            f"  User: {user.username}\n"
            f"  User funds: {user.funds}\n"
            f"  Product: {order.product}\n"
            f"  Quantity: {quantity}\n"
            f"  Direction: {'BUY_UP' if order.direction == order.BUY_UP else 'BUY_DOWN'}\n"
            f"  Order Price: {order.price}\n"
            f"  Settled Price: {order.settled_price}\n"
            f"  Status: {order.status}"
        )

        settled_count += 1
        user.save()

    logger.info(f"Task completed: {settled_count} orders settled.")
    return f"Orders checked and settled: {settled_count}"