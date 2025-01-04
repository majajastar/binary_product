import numpy as np
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapps.prices.models import MinutePrice, FiveMinutePrice, FifteenMinutePrice, HourPrice, DayPrice
import pandas as pd
from functools import lru_cache
from myapps.prices.management.commands.generate_prices import simulate_stock_price, simulate_stock_price_in_range

class Command(BaseCommand):
    help = "Generate day and minute price data for a given date range and store it in the database."

    def add_arguments(self, parser):
        # Adding arguments for start date, start price, range of days, and delta
        parser.add_argument('product_type', type=str, help='Product name')
        parser.add_argument('start_date', type=str, help='Start date in format YYYY-MM-DD')
        parser.add_argument('start_price', type=float, help='Initial start price')
        parser.add_argument('year_return', type=float, help='Average year return')
        parser.add_argument('year_volatility', type=float, help='Average year volatility ')

    def handle(self, *args, **kwargs):
        # Get the arguments passed in the command
        product_type = kwargs['product_type']
        start_date = pd.to_datetime(kwargs['start_date'])
        start_price = kwargs['start_price']
        day_return = kwargs['year_return']
        day_volatility = kwargs['year_volatility']
        range_days = 365
        # Calculate the end date based on the range of days
        end_date = start_date + pd.Timedelta(days=range_days)
        
        # Generate the timestamps for each day in the given range (for DayPrice)
        day_timestamps = pd.date_range(start=start_date, end=end_date, freq='D')  # Daily intervals
        day_prices = simulate_stock_price(start_date, start_price, day_return, day_volatility, 366)
        # print(day_prices, len(day_prices))
        for i,timestamp in enumerate(day_timestamps[:-1]):
            if timezone.is_naive(timestamp):
                timestamp = timezone.make_aware(timestamp)
            timestamp_next = day_timestamps[i+1]
            if timezone.is_naive(timestamp_next):
                timestamp_next = timezone.make_aware(timestamp_next)
            day_price = day_prices[i]
            next_day_price = day_prices[i+1]
            hour_prices = simulate_stock_price_in_range(timestamp, day_price, next_day_price, 25)
            open_price = hour_prices[0]
            close_price = hour_prices[-1]
            high_price = max(hour_prices)
            low_price = min(hour_prices)
            print(timestamp, open_price, close_price, high_price, low_price)
            hour_timestamps = pd.date_range(start=timestamp, end=timestamp_next, freq='H')  # Daily intervals
            #print(len(hour_timestamps), len(hour_prices))
            for i in range(len(hour_timestamps) - 1):
                hour_timestamp = hour_timestamps[i]
                hour_price = hour_prices[i]
                hour_price_next = hour_prices[i+1]
                #print(i, hour_price, hour_price_next)
                HourPrice.objects.update_or_create(
                    product_type=product_type,
                    timestamp=hour_timestamp,
                    defaults={'open': hour_price, 'high': max(hour_price,hour_price_next), 'low':  min(hour_price,hour_price_next), 'close': hour_price_next}
            )

            DayPrice.objects.update_or_create(
                product_type=product_type,
                timestamp=timestamp,
                defaults={'open': open_price, 'high': high_price, 'low': low_price, 'close': close_price}
            )
        self.stdout.write(self.style.SUCCESS(f"Successfully generated and stored day and hour price records for {range_days} days."))
