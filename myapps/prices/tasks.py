# tasks.py
from celery import shared_task
from .tasks_utils import generate_prices
from django.utils import timezone
from datetime import timedelta

@shared_task
def generate_prices_task():
    product_type = "usd-eur"
    current_time = timezone.now().replace(minute=0, second=0, microsecond=0)
    #next_time = (current_time + timedelta(hours=4))
    generate_prices(product_type, current_time)
    #generate_prices(product_type, next_time)