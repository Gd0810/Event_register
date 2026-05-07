from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Count, Sum, Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import Event, Booking
from .forms import EventForm, BookingForm
import json
from datetime import datetime, timedelta


# ─── PUBLIC VIEWS ────────────────────────────────────────────────────────────

def landing(request):
    events = Event.objects.filter(is_active=True).order_by('date')
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    if category:
        events = events.filter(category=category)
    if search:
        events = events.filter(Q(title__icontains=search) | Q(venue__icontains=search))
    categories = Event.CATEGORY_CHOICES
    return render(request, 'events/landing.html', {
        'events': events,
        'categories': categories,
        'selected_category': category,
        'search': search,
    })


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    return render(request, 'events/event_detail.html', {'event': event})


def book_event(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.event = event
            booking.total_price = event.price * booking.quantity
            booking.save()
            # Update available seats
            event.available_seats = max(0, event.available_seats - booking.quantity)
            event.save()
            # Send invoice email
            try:
                send_invoice_email(booking)
            except Exception as e:
                print(f"Email error: {e}")
            return redirect('booking_success', pk=booking.pk)
    else:
        form = BookingForm(initial={'booking_date': timezone.now().date()})
    return render(request, 'events/book_event.html', {'event': event, 'form': form})


def booking_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'events/booking_success.html', {'booking': booking})


def send_invoice_email(booking):
    subject = f'Booking Confirmed – {booking.invoice_number}'
    html_content = render_to_string('events/invoice_email.html', {'booking': booking})
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[booking.customer_email],
    )
    email.content_subtype = 'html'
    email.send()


# ─── DASHBOARD VIEWS ─────────────────────────────────────────────────────────

def send_cancellation_email(booking):
    subject = f'Booking Cancelled - {booking.invoice_number}'
    html_content = f"""
    <h2>Booking Cancelled</h2>
    <p>Hello {booking.customer_name},</p>
    <p>Your booking has been cancelled successfully.</p>
    <p><strong>Invoice No:</strong> {booking.invoice_number}</p>
    <p><strong>Event:</strong> {booking.event.title}</p>
    <p><strong>Date:</strong> {booking.event.date}</p>
    <p><strong>Time:</strong> {booking.event.time}</p>
    <p><strong>Venue:</strong> {booking.event.venue}</p>
    <p><strong>Seats:</strong> {booking.quantity}</p>
    <p><strong>Status:</strong> Cancelled</p>
    <p>Thank you,<br>EventPro</p>
    """
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[booking.customer_email],
    )
    email.content_subtype = 'html'
    email.send()


def dashboard(request):
    total_events = Event.objects.count()
    active_events = Event.objects.filter(is_active=True).count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Recent bookings
    recent_bookings = Booking.objects.select_related('event').order_by('-created_at')[:8]

    # Bookings per event (top 7)
    bookings_per_event = (
        Event.objects.annotate(booking_count=Count('bookings'))
        .order_by('-booking_count')[:7]
    )

    # Monthly revenue (last 6 months)
    months_data = []
    today = timezone.now().date()
    for i in range(5, -1, -1):
        d = today.replace(day=1) - timedelta(days=i * 30)
        month_label = d.strftime('%b %Y')
        rev = Booking.objects.filter(
            status='confirmed',
            created_at__year=d.year,
            created_at__month=d.month
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        months_data.append({'month': month_label, 'revenue': float(rev)})

    # Category distribution
    cat_data = (
        Event.objects.values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    return render(request, 'dashboard/dashboard.html', {
        'total_events': total_events,
        'active_events': active_events,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'bookings_per_event': json.dumps([
            {'name': e.title[:20], 'count': e.booking_count} for e in bookings_per_event
        ]),
        'monthly_revenue': json.dumps(months_data),
        'category_data': json.dumps([
            {'category': d['category'], 'count': d['count']} for d in cat_data
        ]),
    })


def event_list_dashboard(request):
    events = Event.objects.all().order_by('-created_at')
    return render(request, 'dashboard/event_list.html', {'events': events})


def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event created successfully!')
            return redirect('dashboard_events')
    else:
        form = EventForm()
    return render(request, 'dashboard/event_form.html', {'form': form, 'action': 'Create'})


def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('dashboard_events')
    else:
        form = EventForm(instance=event)
    return render(request, 'dashboard/event_form.html', {'form': form, 'action': 'Edit', 'event': event})


def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted.')
        return redirect('dashboard_events')
    return render(request, 'dashboard/event_confirm_delete.html', {'event': event})


def booking_list_dashboard(request):
    bookings = Booking.objects.select_related('event').order_by('-created_at')
    return render(request, 'dashboard/booking_list.html', {'bookings': bookings})


def booking_detail_dashboard(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'dashboard/booking_detail.html', {'booking': booking})


def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        booking.event.available_seats += booking.quantity
        booking.event.save()
        try:
            send_cancellation_email(booking)
        except Exception as e:
            print(f"Cancellation email error: {e}")
        messages.success(request, 'Booking cancelled.')
        return redirect('dashboard_bookings')
    return render(request, 'dashboard/booking_cancel_confirm.html', {'booking': booking})
