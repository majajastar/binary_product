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

# Generate random stock data
def get_60_minute_data(current_time, product_type):
    np.random.seed(42)  # Set seed for reproducibility
    # Calculate the time 60 minutes ago
    time_60_minutes_ago = current_time - timedelta(minutes=60)

    # Find the next settlement time (next multiple of 5 minutes)
    minutes_to_next_settlement = 5 - (current_time.minute % 5)
    next_settlement_time = current_time + timedelta(minutes=minutes_to_next_settlement)
    next_settlement_time = next_settlement_time.replace(second=0, microsecond=0)
    order_deadline_time = next_settlement_time - timedelta(minutes=1)
    tag_time = next_settlement_time - timedelta(minutes=5)

    # Query the records where product_type is 'productA' and the timestamp is less than or equal to tag_time
    tag_price = MinutePrice.objects.filter(
        product_type=product_type,
        timestamp__lte=tag_time  # Filter for records where timestamp is before or at tag_time
    ).order_by('-timestamp').first()  # Get the latest record before or at tag_time
    #print(tag_price.close)
    # Query the records where product_type is 'productA' and within the last 60 minutes
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
    
    #print("current_time:", current_time)
    #print("next_settlement_time:",next_settlement_time)
    #print("order_deadline_time:",order_deadline_time)
    
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
        "open_prices" : open_prices,
        "close_prices" : [0],
        "high_prices" : [0],
        "low_prices" : [0],
        "price_range" : [0, 0],
        "time_range" : [current_time, current_time],
        'product_type': product_type,
        'current_time':  current_time,
        'tag_time':  current_time,
        'tag_price':  0,
        'next_settlement_time': next_settlement_time,
        'order_deadline_time': order_deadline_time  
        }
    price_second = np.random.uniform(low_prices[-1], high_prices[-1], 58).tolist()
    price_second = [open_prices[-1]] + price_second + [close_prices[-1]]
    current_price = price_second[second]
    price_length = max(high_prices) - min(low_prices);
    price_range =  [min(low_prices)- price_length/2, max(high_prices) + price_length/2]
    time_range = [timestamps[0], timestamps[-1] + timedelta(minutes=15)]
    #print(second, price_range, max(price_second[:second+1]))
    # Create a DataFrame with the generated data
    data = {
        "timestamps" : timestamps,
        "open_prices" : open_prices,
        "close_prices" : close_prices[:-1] + [current_price],
        "high_prices" : high_prices[:-1] + [max(price_second[:second+1])],
        "low_prices" : low_prices[:-1] + [min(price_second[:second+1])],
        "price_range" : price_range,
        "time_range" : time_range,
        'product_type': product_type,
        'current_time':  current_time,
        'tag_time':  tag_time,
        'tag_price':  tag_price.close,
        'next_settlement_time': next_settlement_time,
        'order_deadline_time': order_deadline_time
    }
    return data

def get_order_data(request, product_type="ProductA"):
    if not request.user.is_authenticated:
        return JsonResponse({
            "orders": None,
            "has_next": None,
            "has_previous": None,
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
        else:
            profit = float(current_price) - order.price
        if order.direction == order.BUY_DOWN:
            profit = profit * -1

        order_data.append({
            "id": order.id,
            "product": order.product,
            "price": order.price,
            "direction": order.direction,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "settled_at": order.settled_at.strftime("%Y-%m-%d %H:%M:%S") if order.settled_at else None,
            "settled_price": order.settled_price,
            "status": order.status,
            "profit": profit,
        })

    # Paginate the data
    paginator = Paginator(order_data, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return JsonResponse({
        "orders": page_obj.object_list,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
    })


# View to serve updated stock data
def get_product_data(request, product_type):
    # Get the current time
    #print(product_type)
    current_time = timezone.now()
    data = get_60_minute_data(current_time, product_type)
    #print(data)
    return JsonResponse(data)

def product_page(request, product_type="ProductA"):
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