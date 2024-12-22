# admin.py
from django.contrib import admin
from .models import Order
from django.contrib.auth.models import User

class OrderAdmin(admin.ModelAdmin):
    # List the fields to be shown in the admin list view
    list_display = ('user', 'product', 'quantity', 'price', 'settled_price', 'status', 'direction', 'settled_at', 'created_at', 'updated_at')
    
    # Add filters for the admin sidebar (filter by user and status)
    list_filter = ('user', 'status', 'direction', 'settled_at')

    # Add search functionality (search orders by user, product, or status)
    search_fields = ('user__username', 'product', 'status')

    # Allow editing multiple fields directly in the admin list view
    list_editable = ('status', 'settled_price')

    # Allow ordering of orders by specified fields
    ordering = ('-created_at',)  # Default order by creation time (newest first)

    # Add fields that should be visible when creating or editing an order
    fields = ('user', 'product', 'quantity', 'price', 'settled_price', 'status', 'direction', 'settled_at')

    # Make sure user is read-only in the admin (since it's linked to authenticated user)
    readonly_fields = ('user',)

# Register the Order model with the custom admin interface
admin.site.register(Order, OrderAdmin)
