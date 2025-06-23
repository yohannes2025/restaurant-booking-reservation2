from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView # For a default root URL
from bookings import views as bookings_views # Your bookings app views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bookings/', include('bookings.urls')), # Includes your bookings app-specific URLs
    path('accounts/', include('django.contrib.auth.urls')), # Provides login, logout, password reset
    
    # --- THIS IS THE CRITICAL CHANGE ---
    # We directly use the UserRegisterView class and call its .as_view() method
    path('accounts/register/', bookings_views.UserRegisterView.as_view(), name='register'),
    # --- END CRITICAL CHANGE ---

    # Uncommented and using RedirectView for the root URL
    path('', RedirectView.as_view(url='/bookings/', permanent=True)), # Redirect root to service list
]