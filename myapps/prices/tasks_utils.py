# tasks_utils.py
from myapps.prices.models import MinutePrice, FiveMinutePrice, FifteenMinutePrice, HourPrice, DayPrice
import numpy as np
import pandas as pd
from django.utils import timezone
from myapps.prices.management.commands.generate_prices import simulate_stock_price_in_range
import logging
# Get a logger instance
logger = logging.getLogger(__name__)
def generate_prices(product_type, start_date):
    # Implement the core logic here
    print(f"Generating prices for {product_type} starting from {start_date}")
    
    # Calculate the end date based on the range of days
    range_days = 1
    start_date = pd.to_datetime(start_date)
    end_date = start_date + pd.Timedelta(days=range_days)
    
    # Generate the timestamps for each day in the given range (for DayPrice)
    hour_timestamps = pd.date_range(start=start_date, end=end_date, freq='h')  # Daily intervals

    for i, timestamp in enumerate(hour_timestamps[:-1]):
        if timezone.is_naive(timestamp):
            timestamp = timezone.make_aware(timestamp)
        timestamp_next = hour_timestamps[i+1]
        if timezone.is_naive(timestamp_next):
            timestamp_next = timezone.make_aware(timestamp_next)
        hour_price = HourPrice.objects.get(timestamp = timestamp, product_type = product_type)
        minutes_prices = simulate_stock_price_in_range(timestamp, hour_price.open, hour_price.close, 61)
        minute_timestamps = pd.date_range(start=timestamp, end=timestamp_next, freq='min')  # Daily intervals
        #print(i, timestamp, timestamp_next, minutes_prices[0], minutes_prices[-1])
        open_price = minutes_prices[0]
        close_price = minutes_prices[-1]
        high_price = max(minutes_prices)
        low_price = min(minutes_prices)
        logger.info(
            "Index: %s, Current Timestamp: %s, Next Timestamp: %s, Open: %s, Close: %s, High: %s, Low: %s",
            i, timestamp, timestamp_next, open_price, close_price, high_price, low_price
        )
        
        
        HourPrice.objects.update_or_create(
            product_type=product_type,
            timestamp=timestamp,
            defaults={'open': open_price, 'high': high_price, 'low': low_price, 'close': close_price}
        )
        #print(minute_timestamps, len(minute_timestamps))
        for i in range(len(minute_timestamps) - 1):
            minute_timestamp = minute_timestamps[i]
            minute_price = minutes_prices[i]
            minute_price_next = minutes_prices[i+1]
            second_prices = simulate_stock_price_in_range(minute_timestamp, minute_price, minute_price_next, 61, True)
            #print(i,minute_price, minute_price_next, max(second_prices), min(second_prices))
            MinutePrice.objects.update_or_create(
                product_type=product_type,
                timestamp=minute_timestamp,
                defaults={'open': minute_price, 
                          'high': max(second_prices), 
                          'low':  min(second_prices), 
                          'close': minute_price_next}
        )
