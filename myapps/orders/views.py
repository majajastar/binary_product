from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from myapps.orders.models import Order
from django.shortcuts import get_object_or_404
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
import json

@csrf_exempt  # Disable CSRF check for this view (or handle CSRF token on the frontend)
@login_required  # Ensure that only authenticated users can create an order
def create_order(request):
    if request.method == 'POST':
        try:
            current_time = timezone.now()
            minutes_to_next_settlement = 5 - (current_time.minute % 5)
            next_settlement_time = current_time + timedelta(minutes=minutes_to_next_settlement)
            data = json.loads(request.body)
            user = request.user  # Get the current logged-in user
            product_type = data.get('product_type')
            price = float(data.get('price'))  # Ensure price is a float
            action = data.get('action')
            direction = Order.BUY_UP if action == "buy_up" else Order.BUY_DOWN
            quantity = data.get('quantity')
            # Check if user has enough funds
            if user.funds < price*quantity:
                return JsonResponse({'success': False, 'error': '餘額不足'})
            # Deduct the price from the user's funds
            if direction == Order.BUY_UP:
                user.funds -= price*quantity
            else:
                user.funds += price*quantity
            user.save()
            # Create an Order if the user has enough funds
            new_order = Order.objects.create(
                user=user,
                product=product_type,
                quantity=quantity,
                direction=direction,
                price=price,
                settled_at=next_settlement_time,
                status=Order.ACTIVED  # Default status is 'pending'
            )
            redirect_url = reverse('product_page', kwargs={'product_type': product_type})
            return JsonResponse({'success': True, 'order_id': new_order.id, "redirect_url": redirect_url})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


