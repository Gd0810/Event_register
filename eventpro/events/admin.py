from django.contrib import admin
from .models import Event, Booking

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'date', 'price', 'available_seats', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'venue']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer_name', 'event', 'quantity', 'total_price', 'status']
    list_filter = ['status']
    search_fields = ['invoice_number', 'customer_name', 'customer_email']
