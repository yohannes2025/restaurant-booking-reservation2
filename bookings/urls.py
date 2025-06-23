# # bookings/urls.py
# from django.urls import path
# from . import views

# app_name = 'bookings'

# urlpatterns = [
#     # Authentication
#     path('register/', views.UserRegisterView.as_view(), name='register'),

#     # Services
#     path('', views.ServiceListView.as_view(), name='service_list'),
#     path('register/', views.register, name='register'),  # Custom registration
#     path('<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'), # New detail view
#     path('<int:pk>/book/', views.BookServiceView.as_view(), name='book_service'),

#     # Bookings
#     path('my-bookings/', views.UserBookingListView.as_view(), name='user_bookings'),
#     path('booking/<int:pk>/cancel/', views.CancelBookingView.as_view(), name='cancel_booking'),
#     path('booking/success/', views.BookingSuccessView.as_view(), name='booking_success'),

#     # User Profile
#     path('profile/', views.UserProfileView.as_view(), name='user_profile'),
#     path('profile/edit/', views.UserProfileUpdateView.as_view(), name='edit_user_profile'),

#     # AJAX for available slots (optional)
#     path('api/slots/<int:service_id>/', views.get_available_slots_ajax, name='api_available_slots'),
# ]


# bookings/urls.py

from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegisterView.as_view(), name='register'),

    # Services
    path('', views.ServiceListView.as_view(), name='service_list'),

    path('<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),

    path('<int:pk>/book/', views.BookServiceView.as_view(), name='book_service'),

    # User Bookings
    path('my-bookings/', views.UserBookingListView.as_view(), name='user_bookings'),
    path('booking/<int:pk>/cancel/', views.CancelBookingView.as_view(), name='cancel_booking'),
    path('booking/success/', views.BookingSuccessView.as_view(), name='booking_success'),

    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='edit_user_profile'),

    # AJAX for available slots (optional - for customer-facing booking)
    path('api/slots/<int:service_id>/', views.get_available_slots_ajax, name='api_available_slots'),

    # --- Staff Dashboard URLs ---
    path('staff/', views.StaffDashboardView.as_view(), name='staff_dashboard'),

    # Table Management (Staff)
    path('staff/tables/', views.TableListView.as_view(), name='staff_table_list'),
    path('staff/tables/add/', views.TableCreateView.as_view(), name='staff_table_add'),
    path('staff/tables/<int:pk>/', views.TableDetailView.as_view(), name='staff_table_detail'),
    path('staff/tables/<int:pk>/edit/', views.TableUpdateView.as_view(), name='staff_table_edit'),
    path('staff/tables/<int:pk>/delete/', views.TableDeleteView.as_view(), name='staff_table_delete'),

    # Booking Management (Staff)
    path('staff/bookings/', views.StaffBookingListView.as_view(), name='staff_booking_list'),
    path('staff/bookings/<int:pk>/', views.StaffBookingDetailView.as_view(), name='staff_booking_detail'),

    # Use POST for actions
    path('staff/bookings/<int:pk>/action/', views.StaffBookingActionView.as_view(), name='staff_booking_action'),

    # Calendar View (Staff)
    path('staff/calendar/', views.BookingCalendarView.as_view(), name='staff_calendar'),

    # API endpoint for FullCalendar events
    path('staff/api/calendar-events/', views.BookingCalendarAPIView.as_view(), name='staff_calendar_api_events'),

]