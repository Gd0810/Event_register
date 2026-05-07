# EventPro – Django Event Registration System

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Gmail (for invoice emails)
Edit `core/settings.py` and update:
```python
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_gmail_app_password'   # Not your normal password!
DEFAULT_FROM_EMAIL = 'EventPro <your_email@gmail.com>'
```
> To get a Gmail App Password: Google Account → Security → 2-Step Verification → App passwords

### 3. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create superuser (for /admin)
```bash
python manage.py createsuperuser
```

### 5. Start the server
```bash
python manage.py runserver
```

## URLs
| URL | Description |
|-----|-------------|
| `/` | Public landing page – all events |
| `/event/<id>/` | Event detail page |
| `/event/<id>/book/` | Booking form |
| `/booking/<id>/success/` | Booking success + invoice |
| `/dashboard/` | Analytics overview |
| `/dashboard/events/` | CRUD events |
| `/dashboard/bookings/` | View/cancel bookings |
| `/admin/` | Django admin |

## Features
- 🎫 Event listing with category filters & search
- 📋 Booking form with live price calculation
- 📧 Automatic invoice email on booking
- 📊 Dashboard with Chart.js visualizations:
  - Monthly revenue (line chart)
  - Bookings per event (bar chart)
  - Category distribution (donut chart)
- ✏️ Full CRUD for events (title, photo, price, seats, date, time)
- 🗂️ Booking management with cancel functionality
