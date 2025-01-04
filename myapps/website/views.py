import numpy as np
import pandas as pd
from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.utils import timezone
from myapps.prices.models import MinutePrice
from myapps.orders.models import Order
from django.core.paginator import Paginator
from .models import ContactMethod
from myapps.prices.management.commands.generate_prices import simulate_stock_price
from functools import lru_cache

@lru_cache(maxsize=128)
def get_60_seconds_data(timestamp, start_price, end_price, max_price, min_price, periods):
    np.random.seed(int(timestamp.timestamp()))  # Set seed for reproducibility
    # Time increments
    dt = 1 / periods  # Assuming normalized time
    
    drift = (end_price-start_price)/start_price
    volatility = drift*5
    
    # Simulate Brownian motion
    prices = [start_price]
    for t in range(periods):
        # Calculate random change
        random_shock = np.random.normal(0, 1) * np.sqrt(dt)
        drift_adjustment = drift * dt
        stochastic_part = volatility * random_shock
        
        # Update price
        next_price = prices[-1] * np.exp(drift_adjustment + stochastic_part)
        
        # Clip to max/min price
        next_price = np.clip(next_price, min_price, max_price)
        prices.append(next_price)
    
    # Adjust to trend towards end_price
    scaling_factor = end_price / prices[-1]
    
    prices_cor = []
    for i,p in enumerate(prices):
        p_scaled = p * scaling_factor
        diff = p_scaled - p
        mul = i/(len(prices) - 1)
        prices_cor.append(p + diff * mul)
    
    return prices_cor[:-1]

# Generate random stock data
def get_60_minute_data(current_time, product_type):
    np.random.seed(42)  # Set seed for reproducibility
    # Calculate the time 60 minutes ago
    time_60_minutes_ago = current_time - timedelta(minutes=60)
    time_60_seconds = [current_time - timedelta(seconds=i) for i in range(59,-1,-1)]

    # Find the next settlement time (next multiple of 5 minutes)
    minutes_to_next_settlement = 5 - (current_time.minute % 5)
    next_settlement_time = current_time + timedelta(minutes=minutes_to_next_settlement)
    next_settlement_time = next_settlement_time.replace(second=0, microsecond=0)
    order_deadline_time = next_settlement_time - timedelta(minutes=1)
    tag_time = next_settlement_time - timedelta(minutes=5)

    # Query the records where product_type is 'usd-eur' and the timestamp is less than or equal to tag_time
    tag_price = MinutePrice.objects.filter(
        product_type=product_type,
        timestamp__lte=tag_time  # Filter for records where timestamp is before or at tag_time
    ).order_by('-timestamp').first()  # Get the latest record before or at tag_time
    #print(tag_price.close)
    # Query the records where product_type is 'usd-eur' and within the last 60 minutes
    latest_60_minutes_records = MinutePrice.objects.filter(
        product_type=product_type, 
        timestamp__gte=time_60_minutes_ago
    ).order_by('timestamp')[:60][::-1]
    # Iterate over the results and print them
    timestamps = []
    open_prices = []
    close_prices = []
    high_prices = []
    low_prices = []
    
    for price in latest_60_minutes_records[::-1]:
        timestamps.append(price.timestamp)
        open_prices.append(price.open)
        high_prices.append(price.high)
        low_prices.append(price.low)
        close_prices.append(price.close)

    
    # Extract only the seconds field
    second = current_time.second
    if not low_prices or not high_prices:
        return {
        "timestamps" : timestamps,
        "time_60_seconds" : time_60_seconds,
        "open_prices" : open_prices,
        "close_prices" : [0],
        "high_prices" : [0],
        "low_prices" : [0],
        "price_range" : [0, 0],
        "time_range" : [current_time, current_time],
        "time_second_range": [current_time, current_time],
        'product_type': product_type,
        'current_time':  current_time,
        'tag_time':  current_time,
        'tag_price':  0,
        'next_settlement_time': next_settlement_time,
        'order_deadline_time': order_deadline_time,
        'price_60_second': [0],
        'digit' : 6
        }
    price_second = get_60_seconds_data(timestamps[-1],open_prices[-1],close_prices[-1],high_prices[-1],low_prices[-1],60)

    price_prev_second = get_60_seconds_data(timestamps[-2],open_prices[-2],close_prices[-2],high_prices[-2],low_prices[-2],60)

    price_60_second = price_prev_second[-(60-second):] + price_second[0:second]

    current_price = price_second[second]
    price_length = max(high_prices) - min(low_prices)
    price_range =  [min(low_prices)- price_length/2, max(high_prices) + price_length/2]

    price_second_length = max(price_60_second) - min(price_60_second)
    price_second_range = [min(price_60_second)- price_second_length/2, max(price_60_second) + price_second_length/2]

    time_range = [timestamps[0], timestamps[-1] + timedelta(minutes=15)]
    time_second_range = [time_60_seconds[0],time_60_seconds[-1] + timedelta(seconds=15)]

    price_diff = price_range[1] - price_range[0]
    if price_diff < 0.0001:
        digit = 8
    elif price_diff < 0.001:
        digit = 7
    elif price_diff < 0.01:
        digit = 6
    elif price_diff < 0.1:
        digit = 5
    elif price_diff < 1:
        digit = 4
    elif price_diff < 10:
        digit = 3
    else:
        digit = 2
    # Create a DataFrame with the generated data
    data = {
        "timestamps" : timestamps,
        "time_60_seconds" : time_60_seconds,
        "open_prices" : open_prices,
        "close_prices" : close_prices[:-1] + [current_price],
        "high_prices" : high_prices[:-1] + [max(price_second[:second+1])],
        "low_prices" : low_prices[:-1] + [min(price_second[:second+1])],
        "price_range" : price_range,
        "price_second_range": price_second_range,
        "time_range" : time_range,
        "time_second_range": time_second_range,
        'product_type': product_type,
        'current_time':  current_time,
        'tag_time':  tag_time,
        'tag_price':  tag_price.close,
        'next_settlement_time': next_settlement_time,
        'order_deadline_time': order_deadline_time,
        'price_60_second': price_60_second,
        'digit' : digit
    }
    return data

def get_order_data(request, product_type="usd-eur"):
    if not request.user.is_authenticated:
        return JsonResponse({
            "orders": None,
            "has_next": None,
            "has_previous": None,
            "digit": 2,
        })
    # Fetch the orders for the authenticated user and product
    orders = Order.objects.filter(user=request.user, product=product_type)
    current_price = request.GET.get('current_price')
    # Add profit data
    order_data = []
    for order in orders:
        # Calculate profit if the order is settled; otherwise, default to None
        if order.status == Order.COMPLETED:
            profit = order.settled_price - order.price
            profit*=order.quantity
        else:
            if current_price == 0:
                profit = "-"
            else:
                profit = float(current_price) - order.price
                profit*=order.quantity
        if order.direction == order.BUY_DOWN:
            profit = profit * -1
        order_data.append({
            "id": order.id,
            "product": order.product,
            "price": order.price,
            "quantity": order.quantity,
            "direction": order.direction,
            "created_at": order.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "settled_at": order.settled_at.strftime("%Y-%m-%dT%H:%M:%SZ") if order.settled_at else None,
            "settled_price": order.settled_price,
            "status": order.status,
            "profit": profit,
        })

    # Paginate the data
    paginator = Paginator(order_data, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    digit = 6
    if abs(profit) < 0.0001:
        digit = 8
    elif abs(profit) < 0.001:
        digit = 7
    elif abs(profit) < 0.01:
        digit = 6
    elif abs(profit) < 0.1:
        digit = 5
    elif abs(profit) < 1:
        digit = 4
    elif abs(profit) < 10:
        digit = 3
    else:
        digit = 2
    return JsonResponse({
        "orders": page_obj.object_list,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "digit":digit,
    })


# View to serve updated stock data
def get_product_data(request, product_type):
    # Get the current time
    #print(product_type)
    current_time = timezone.now()
    data = get_60_minute_data(current_time, product_type)
    #print(data)
    return JsonResponse(data)

def product_page(request, product_type="usd-eur"):
    current_time = timezone.now()
    data = get_60_minute_data(current_time, product_type)
    name = "二元智选"

    return render(request, 'product.html', {'name': name, 'data': data, 'product_type':product_type})

def about_us(request):
    name = "二元智选"

    return render(request, 'about_us.html', {'name': name})

def contact_us(request):
    name = "二元智选"
    # Query the latest 3 ContactMethod entries ordered by their ID (descending)
    latest_contacts = ContactMethod.objects.all().order_by('-id')[:3]

    return render(request, 'contact_us.html', {'name': name, 'latest_contacts': latest_contacts})