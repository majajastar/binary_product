import numpy as np
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapps.prices.models import MinutePrice, FiveMinutePrice, FifteenMinutePrice, HourPrice, DayPrice
import pandas as pd

class Command(BaseCommand):
    help = "Generate day and minute price data for a given date range and store it in the database."

    def add_arguments(self, parser):
        # Adding arguments for start date, start price, range of days, and delta
        parser.add_argument('product_type', type=str, help='Product name')
        parser.add_argument('start_date', type=str, help='Start date in format YYYY-MM-DD')
        parser.add_argument('start_price', type=float, help='Initial start price')
        parser.add_argument('range_days', type=int, help='Duration in days to generate data')
        parser.add_argument('delta', type=float, help='Delta to control the chaos of price fluctuation')

    def handle(self, *args, **kwargs):
        # Get the arguments passed in the command
        product_type = kwargs['product_type']
        start_date = pd.to_datetime(kwargs['start_date'])
        start_price = kwargs['start_price']
        range_days = kwargs['range_days']
        delta = kwargs['delta']

        # Calculate the end date based on the range of days
        end_date = start_date + pd.Timedelta(days=range_days)

        # Generate the timestamps for each day in the given range (for DayPrice)
        day_timestamps = pd.date_range(start=start_date, end=end_date, freq='D')  # Daily intervals
        open_price = start_price + np.random.uniform(delta * -1, delta)
        # Generate price data for each day
        for timestamp in day_timestamps:
            # Ensure the timestamp is timezone-aware
            if timezone.is_naive(timestamp):
                timestamp = timezone.make_aware(timestamp)


            close_price = open_price + np.random.uniform(delta * -1, delta)

            # Generate minute-based data for the day (MinutePrice)
            minute_timestamps = pd.date_range(start=timestamp, periods=1440, freq='T')  # 1440 minutes in a day

            base_series = np.linspace(open_price, close_price, 1441)

            minute_prices = []
            for price in base_series:
                minute_prices.append(np.random.normal(price, price*0.01))
            minute_prices[0] = start_price
            minute_prices[-1] = close_price

            # minute_prices = base_series
            # minute_prices = np.random.uniform(low_price, high_price, 1439)
            # minute_prices = minute_prices.tolist()
            # minute_prices = np.array([start_price] + minute_prices + [close_price])
            
            high_minutes = []
            low_minutes = []
            for i, minute_timestamp in enumerate(minute_timestamps[:-1]):
                #print(i, minute_timestamp)
                # Ensure the timestamp is timezone-aware
                if timezone.is_naive(minute_timestamp):
                    minute_timestamp = timezone.make_aware(minute_timestamp)

                # Get the price for this minute, ensuring it's within the [open, close] range
                price = minute_prices[i]
                price_next = minute_prices[i+1]

                # Generate the high and low prices for the minute
                high_minute = max(price,price_next) + max(np.random.normal(0, delta/ 5), 0)
                low_minute = min(price,price_next) - max(np.random.normal(0, delta/5), 0)
                print ("X:", price, price_next, high_minute, low_minute)
                high_minutes.append(high_minute)
                low_minutes.append(low_minute)
                continue
                if i%5 == 0:
                    price_5 = minute_prices[i]
                    price_5_next = minute_prices[i+5]
                    high_5_minute = max(high_minutes[-5:])
                    low_5_minute = min(low_minutes[-5:])
                    # Generate the high and low prices for the minute
                    # Save the generated minute data (MinutePrice)
                    FiveMinutePrice.objects.update_or_create(
                        product_type=product_type,
                        timestamp=minute_timestamp,
                        defaults={'open': price_5, 'high': high_5_minute, 'low': low_5_minute, 'close': price_5_next}
                    )
                if i%15 == 0:
                    price_15 = minute_prices[i]
                    price_15_next = minute_prices[i+15]
                    high_15_minute = max(high_minutes[-15:])
                    low_15_minute = min(low_minutes[-15:])
                    # Generate the high and low prices for the minute
                    # Save the generated minute data (MinutePrice)
                    FifteenMinutePrice.objects.update_or_create(
                        product_type=product_type,
                        timestamp=minute_timestamp,
                        defaults={'open': price_15, 'high': high_15_minute, 'low': low_15_minute, 'close': price_15_next}
                    )
                if i%60 == 0:
                    price_60 = minute_prices[i]
                    price_60_next = minute_prices[i+60]
                    high_60_minute = max(high_minutes[-60:])
                    low_60_minute = min(low_minutes[-60:])
                    # Generate the high and low prices for the minute
                    # Save the generated minute data (MinutePrice)
                    HourPrice.objects.update_or_create(
                        product_type=product_type,
                        timestamp=minute_timestamp,
                        defaults={'open': price_60, 'high': high_60_minute, 'low': low_60_minute, 'close': price_60_next}
                    )
                # Save the generated minute data (MinutePrice)
                MinutePrice.objects.update_or_create(
                    product_type=product_type,
                    timestamp=minute_timestamp,
                    defaults={'open': price, 'high': high_minute, 'low': low_minute, 'close': price_next}
                )


                self.stdout.write(self.style.SUCCESS(f"Successfully generated and stored minute price records for {minute_timestamp}"))
            high_price = max(high_minutes)
            low_price = min(low_minutes)
            print(start_price, close_price, high_price, low_price)
            # Save daily price data (DayPrice)
            DayPrice.objects.update_or_create(
                product_type=product_type,
                timestamp=timestamp,
                defaults={'open': open_price, 'high': high_price, 'low': low_price, 'close': close_price}
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully generated and stored day price records for {timestamp}"))
            # Update start_price for the next day
            
            open_price = close_price
        self.stdout.write(self.style.SUCCESS(f"Successfully generated and stored day and minute price records for {range_days} days."))
