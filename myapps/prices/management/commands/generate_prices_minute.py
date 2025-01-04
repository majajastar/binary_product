import numpy as np
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapps.prices.models import MinutePrice, FiveMinutePrice, FifteenMinutePrice, HourPrice, DayPrice
import pandas as pd
from functools import lru_cache
from myapps.prices.management.commands.generate_prices import simulate_stock_price_in_range

class Command(BaseCommand):
    help = "Generate day and minute price data for a given date range and store it in the database."

    def add_arguments(self, parser):
        # Adding arguments for start date, start price, range of days, and delta
        parser.add_argument('product_type', type=str, help='Product name')
        parser.add_argument('start_date', type=str, help='Start date in format YYYY-MM-DD')

    def handle(self, *args, **kwargs):
        # Get the arguments passed in the command
        product_type = kwargs['product_type']
        start_date = pd.to_datetime(kwargs['start_date'])
        # Calculate the end date based on the range of days
        range_days = 1
        end_date = start_date + pd.Timedelta(days=range_days)
        
        # Generate the timestamps for each day in the given range (for DayPrice)
        hour_timestamps = pd.date_range(start=start_date, end=end_date, freq='H')  # Daily intervals
        print(hour_timestamps)
        for i, timestamp in enumerate(hour_timestamps[:-1]):
            if timezone.is_naive(timestamp):
                timestamp = timezone.make_aware(timestamp)
            timestamp_next = hour_timestamps[i+1]
            if timezone.is_naive(timestamp_next):
                timestamp_next = timezone.make_aware(timestamp_next)
            hour_price = HourPrice.objects.get(timestamp = timestamp, product_type = product_type)
            minutes_prices = simulate_stock_price_in_range(timestamp, hour_price.open, hour_price.close, 61)
            print(i, timestamp, timestamp_next, minutes_prices[0], minutes_prices[-1])
            open_price = minutes_prices[0]
            close_price = minutes_prices[-1]
            high_price = max(minutes_prices)
            low_price = min(minutes_prices)
            print(open_price,close_price,high_price,low_price)
            minute_timestamps = pd.date_range(start=timestamp, end=timestamp_next, freq='min')  # Daily intervals
            
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
                second_prices = simulate_stock_price_in_range(minute_timestamp, minute_price, minute_price_next, 61)
                #print(i,minute_price, minute_price_next, max(second_prices), min(second_prices))
                MinutePrice.objects.update_or_create(
                    product_type=product_type,
                    timestamp=minute_timestamp,
                    defaults={'open': minute_price, 
                              'high': max(second_prices), 
                              'low':  min(second_prices), 
                              'close': minute_price_next}
            )
        self.stdout.write(self.style.SUCCESS(f"Successfully generated and stored day and minute price records for {range_days} days."))
