from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.landing, name='landing'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/<int:pk>/book/', views.book_event, name='book_event'),
    path('booking/<int:pk>/success/', views.booking_success, name='booking_success'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/events/', views.event_list_dashboard, name='dashboard_events'),
    path('dashboard/events/create/', views.event_create, name='event_create'),
    path('dashboard/events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('dashboard/events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('dashboard/bookings/', views.booking_list_dashboard, name='dashboard_bookings'),
    path('dashboard/bookings/<int:pk>/', views.booking_detail_dashboard, name='booking_detail'),
    path('dashboard/bookings/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
]
