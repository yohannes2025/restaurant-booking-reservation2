# # bookings/models.py
# from django.db import models
# from django.contrib.auth.models import User
# from django.urls import reverse
# from django.utils import timezone
# from datetime import timedelta

# class Service(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     duration_minutes = models.IntegerField(help_text="Duration of the service in minutes")
#     # New: Max concurrent bookings for this service at any given time slot
#     max_bookings_per_slot = models.IntegerField(default=1, help_text="Maximum number of bookings allowed for this service at the same time slot.")
#     is_available = models.BooleanField(default=True)

#     def __str__(self):
#         return self.name

#     def get_absolute_url(self):
#         return reverse('bookings:service_detail', args=[str(self.id)])

# class Booking(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField()
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('confirmed', 'Confirmed'),
#         ('cancelled', 'Cancelled'),
#         ('completed', 'Completed'),
#     ]
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         # We'll handle collision logic in views for max_bookings_per_slot
#         # For max_bookings_per_slot > 1, unique_together might not be suitable
#         # unique_together = ('service', 'start_time', 'end_time') # Keep if max_bookings_per_slot is always 1

#         # Ordering for better display
#         ordering = ['start_time']

#     def __str__(self):
#         return f"{self.user.username} - {self.service.name} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"

#     def get_absolute_url(self):
#         return reverse('bookings:user_bookings') # Or a detail page for booking

#     @property
#     def is_upcoming(self):
#         return self.start_time > timezone.now()

#     @property
#     def can_cancel(self):
#         # Allow cancellation if pending and more than X hours before start_time
#         return self.status == 'pending' and self.start_time > (timezone.now() + timedelta(hours=1)) # Example: 1 hour cancellation window

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone_number = models.CharField(max_length=20, blank=True, null=True)
#     address = models.TextField(blank=True, null=True)
#     # Add other profile fields as needed

#     def __str__(self):
#         return self.user.username

# bookings/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(help_text="Duration of the service in minutes")
    max_bookings_per_slot = models.IntegerField(default=1, help_text="Maximum number of bookings allowed for this service at the same time slot.")
    is_available = models.BooleanField(default=True)
    # New: Optional link to a Table type or specific table if a service is table-dependent
    # For now, we'll keep Service and Table somewhat separate for simpler table management.
    # If a Service is a 'Table Booking', you might want to link it to specific Tables or a 'Table Type'
    # e.g., table_capacity = models.IntegerField(default=2)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bookings:service_detail', args=[str(self.id)])

class Table(models.Model):
    """Represents a physical table that can be booked."""
    name = models.CharField(max_length=100, unique=True, help_text="e.g., Table 1, Window Table")
    capacity = models.IntegerField(help_text="Maximum number of people this table can seat.")
    is_available = models.BooleanField(default=True, help_text="Is this table generally available for booking?")
    location = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Main Dining Area, Terrace")

    def __str__(self):
        return f"{self.name} (Capacity: {self.capacity})"

    def get_absolute_url(self):
        return reverse('bookings:table_detail', args=[str(self.id)]) # New URL for table detail

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    # New: Optional link to a specific table for this booking
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True,
                              help_text="The specific table assigned to this booking (if applicable).")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # If you always link to a table and want to prevent double-booking the *same* table:
    # unique_together = ('table', 'start_time', 'end_time') # Careful if table can be null or multiple bookings on same table

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        table_info = f" (Table: {self.table.name})" if self.table else ""
        return f"{self.user.username} - {self.service.name} {table_info} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def get_absolute_url(self):
        return reverse('bookings:user_bookings')

    @property
    def is_upcoming(self):
        return self.start_time > timezone.now()

    @property
    def can_cancel(self):
        return self.status == 'pending' and self.start_time > (timezone.now() + timedelta(hours=1))

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username