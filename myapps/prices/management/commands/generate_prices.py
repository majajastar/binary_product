import numpy as np
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapps.prices.models import MinutePrice, FiveMinutePrice, FifteenMinutePrice, HourPrice, DayPrice
import pandas as pd
from functools import lru_cache

def simulate_stock_price_in_range(timestamp, open, close, period):
    seed = int(timestamp.replace(second=0).timestamp())
    rng = np.random.default_rng(seed)
    mu = (close-open)/open
    sigma = mu * rng.uniform(0, 1)
    prices = simulate_stock_price(timestamp, open, mu, sigma, period)
    scaling_factor = close/prices[-1]
    prices_cor = []
    for i,p in enumerate(prices):
        p_scaled = p * scaling_factor
        diff = p_scaled - p
        mul = i/(len(prices) - 1)
        prices_cor.append(p + diff * mul)
    # print("---", open_price,close_price,high_price,low_price, prices_cor[-2], seed)
    return prices_cor

@lru_cache(maxsize=128)
def simulate_stock_price(timestamp, initial_price, mu, sigma, time_steps):
    # Generate random walk (random noise)
    seed = int(timestamp.replace(second=0).timestamp())
    rng = np.random.default_rng(seed)
    dt = 1/time_steps
    epsilon = rng.normal(0, 1, time_steps)
    # List to store the stock prices
    prices = [initial_price]
    # Simulate the stock price over time
    for i in range(1, time_steps):
        # Apply the Geometric Brownian Motion formula
        price = prices[-1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * epsilon[i] * np.sqrt(dt))
        prices.append(price)
    
    return prices

class Command(BaseCommand):
    help = "Generate day and minute price data for a given date range and store it in the database."

    def add_arguments(self, parser):
        # Adding arguments for start date, start price, range of days, and delta
        parser.add_argument('product_type', type=str, help='Product name')
        parser.add_argument('start_date', type=str, help='Start date in format YYYY-MM-DD')
        parser.add_argument('start_price', type=float, help='Initial start price')
        parser.add_argument('range_days', type=int, help='Duration in days to generate data')
        parser.add_argument('average_day_return', type=float, help='Average day return')
        parser.add_argument('average_day_volatility', type=float, help='Average day volatility ')

    def handle(self, *args, **kwargs):
        # Get the arguments passed in the command
        product_type = kwargs['product_type']
        start_date = pd.to_datetime(kwargs['start_date'])
        start_price = kwargs['start_price']
        range_days = kwargs['range_days']
        day_return = kwargs['average_day_return']
        day_volatility = kwargs['average_day_volatility']

        # Calculate the end date based on the range of days
        end_date = start_date + pd.Timedelta(days=range_days)
        
        # Generate the timestamps for each day in the given range (for DayPrice)
        day_timestamps = pd.date_range(start=start_date, end=end_date, freq='D')  # Daily intervals
        initial_price = start_price
        # Generate price data for each day
        for timestamp in day_timestamps:
            # Ensure the timestamp is timezone-aware
            if timezone.is_naive(timestamp):
                timestamp = timezone.make_aware(timestamp)

            # Generate minute-based data for the day (MinutePrice)
            minute_timestamps = pd.date_range(start=timestamp, periods=1441, freq='min')  # 1440 minutes in a day

            mu = np.random.normal(day_return , day_return)
            sigma = np.random.normal(day_volatility , day_volatility)

            time_steps = 1441

            minute_prices = simulate_stock_price(initial_price, mu, sigma, time_steps, 1/time_steps)

            open_price = minute_prices[0]
            close_price = minute_prices[-1]
            initial_price = close_price
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
                middle = (price+price_next)/2
                noise = day_return/144
                high_minute = max(price,price_next) + max(np.random.normal(0, noise*middle), 0)
                low_minute = min(price,price_next) - max(np.random.normal(0, noise*middle), 0)
                #print ("X:", price, price_next, high_minute, low_minute)
                high_minutes.append(high_minute)
                low_minutes.append(low_minute)
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


                # self.stdout.write(self.style.SUCCESS(f"Successfully generated and stored minute price records for {minute_timestamp}"))
            high_price = max(high_minutes)
            low_price = min(low_minutes)
            #(open_price, close_price, high_price, low_price)
            # Save daily price data (DayPrice)
            DayPrice.objects.update_or_create(
                product_type=product_type,
                timestamp=timestamp,
                defaults={'open': open_price, 'high': high_price, 'low': low_price, 'close': close_price}
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully generated and stored day price records for {timestamp}"))
            # Update start_price for the next day
            
            initial_price = close_price
        self.stdout.write(self.style.SUCCESS(f"Successfully generated and stored day and minute price records for {range_days} days."))
