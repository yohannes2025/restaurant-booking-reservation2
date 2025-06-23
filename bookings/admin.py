# # bookings/admin.py
# from django.contrib import admin
# from .models import Service, Booking, UserProfile

# @admin.register(Service)
# class ServiceAdmin(admin.ModelAdmin):
#     list_display = ('name', 'price', 'duration_minutes', 'max_bookings_per_slot', 'is_available')
#     list_filter = ('is_available',)
#     search_fields = ('name', 'description',)

# @admin.register(Booking)
# class BookingAdmin(admin.ModelAdmin):
#     list_display = ('user', 'service', 'start_time', 'end_time', 'status', 'created_at')
#     list_filter = ('status', 'service', 'start_time')
#     search_fields = ('user__username', 'service__name')
#     date_hierarchy = 'start_time'
#     raw_id_fields = ('user', 'service') # Useful for many-to-one fields with many instances

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'phone_number', 'address')
#     search_fields = ('user__username', 'phone_number')

# bookings/admin.py
from django.contrib import admin
from .models import Service, Booking, UserProfile, Table # Import Table

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_minutes', 'max_bookings_per_slot', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name', 'description',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'table', 'start_time', 'end_time', 'status', 'created_at') # Add 'table'
    list_filter = ('status', 'service', 'table', 'start_time') # Add 'table'
    search_fields = ('user__username', 'service__name', 'table__name') # Add 'table__name'
    date_hierarchy = 'start_time'
    raw_id_fields = ('user', 'service', 'table') # Add 'table'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'phone_number')

@admin.register(Table) # Register the Table model
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'is_available', 'location')
    list_filter = ('is_available', 'capacity', 'location')
    search_fields = ('name', 'location')
    ordering = ('name',)