# # bookings/views.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView
# from django.urls import reverse_lazy, reverse
# from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.contrib import messages
# from django.http import JsonResponse
# from django.utils import timezone
# from datetime import timedelta, datetime
# import calendar # For calendar operations
# from .utils import send_booking_confirmation_email


# # Import forms
# from .forms import BookingForm, ServiceSearchForm, UserProfileForm, UserRegisterForm
# from .models import Service, Booking, UserProfile

# # --- Authentication Views ---
# class UserRegisterView(FormView):
#     template_name = 'registration/register.html'
#     form_class = UserRegisterForm
#     success_url = reverse_lazy('login') # Redirect to login after successful registration

#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         service = form.instance.service
#         start_time = form.cleaned_data['start_time']

#         end_time = start_time + timedelta(minutes=service.duration_minutes)
#         form.instance.end_time = end_time

#         if start_time < timezone.now():
#             form.add_error('start_time', "Cannot book a service in the past.")
#             return self.form_invalid(form)

#         overlapping_bookings_count = Booking.objects.filter(
#             service=service,
#             status__in=['pending', 'confirmed'],
#             start_time__lt=end_time,
#             end_time__gt=start_time
#         ).count()

#         if overlapping_bookings_count >= service.max_bookings_per_slot:
#             form.add_error(None, "This time slot is fully booked. Please choose another time.")
#             messages.error(self.request, "This time slot is fully booked. Please choose another time.")
#             return self.form_invalid(form)

#         # Save the booking first
#         response = super().form_valid(form) # This saves form.instance (the booking)

#         # Queue the email sending task after successful booking
#         # Pass the booking's ID to the background task
#         send_booking_confirmation_email.delay(self.object.id) # self.object is the newly created booking

#         messages.success(self.request, f"Your booking for {service.name} at {start_time.strftime('%Y-%m-%d %H:%M')} has been placed. A confirmation email will be sent shortly.")
#         return response

#     def form_invalid(self, form):
#         messages.error(self.request, "There was an error with your registration. Please correct the errors below.")
#         return super().form_invalid(form)

# # --- Service Views ---
# class ServiceListView(ListView):
#     model = Service
#     template_name = 'bookings/service_list.html'
#     context_object_name = 'services'
#     paginate_by = 10 # Optional: Add pagination

#     def get_queryset(self):
#         queryset = super().get_queryset().filter(is_available=True)
#         form = ServiceSearchForm(self.request.GET)
#         if form.is_valid():
#             query = form.cleaned_data.get('query')
#             if query:
#                 queryset = queryset.filter(name__icontains=query)
#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['search_form'] = ServiceSearchForm(self.request.GET)
#         return context

# class ServiceDetailView(DetailView):
#     model = Service
#     template_name = 'bookings/service_detail.html'
#     context_object_name = 'service'

# # --- Booking Views ---
# class BookServiceView(LoginRequiredMixin, CreateView):
#     model = Booking
#     form_class = BookingForm
#     template_name = 'bookings/book_service.html'
#     success_url = reverse_lazy('bookings:booking_success')

#     def get_initial(self):
#         initial = super().get_initial()
#         service = get_object_or_404(Service, pk=self.kwargs['pk'])
#         initial['service'] = service
#         return initial

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['service'] = get_object_or_404(Service, pk=self.kwargs['pk'])
#         return kwargs

#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         service = form.instance.service
#         start_time = form.cleaned_data['start_time']

#         # Calculate end_time based on service duration
#         end_time = start_time + timedelta(minutes=service.duration_minutes)
#         form.instance.end_time = end_time

#         # Ensure booking is not in the past (handled by form clean_start_time too)
#         if start_time < timezone.now():
#             form.add_error('start_time', "Cannot book a service in the past.")
#             return self.form_invalid(form)

#         # Check for slot availability based on max_bookings_per_slot
#         # Count existing confirmed/pending bookings that overlap with the requested slot
#         overlapping_bookings_count = Booking.objects.filter(
#             service=service,
#             status__in=['pending', 'confirmed'],
#             start_time__lt=end_time,
#             end_time__gt=start_time
#         ).count()

#         if overlapping_bookings_count >= service.max_bookings_per_slot:
#             form.add_error(None, "This time slot is fully booked. Please choose another time.")
#             messages.error(self.request, "This time slot is fully booked. Please choose another time.")
#             return self.form_invalid(form)

#         messages.success(self.request, f"Your booking for {service.name} at {start_time.strftime('%Y-%m-%d %H:%M')} has been placed.")
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         service = get_object_or_404(Service, pk=self.kwargs['pk'])
#         context['service'] = service

#         # Logic to generate available time slots for today and next few days
#         # This can be refined with AJAX for dynamic loading
#         today = timezone.localdate()
#         available_slots = []
#         for i in range(7): # Next 7 days
#             day = today + timedelta(days=i)
#             slots_for_day = self._generate_available_slots(service, day)
#             if slots_for_day:
#                 available_slots.append({'date': day, 'slots': slots_for_day})

#         context['available_slots'] = available_slots
#         return context

#     def _generate_available_slots(self, service, date):
#         # This is a placeholder for actual business hours logic
#         # For simplicity, let's assume availability from 9 AM to 5 PM
#         start_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time().replace(hour=9)))
#         end_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time().replace(hour=17))) # 5 PM

#         # Ensure we don't show past slots for today
#         if date == timezone.localdate():
#             if timezone.now() > start_of_day:
#                 start_of_day = timezone.now().replace(minute=0, second=0, microsecond=0) # Round to nearest hour
#                 if start_of_day.hour >= 17: # If it's already past 5 PM, no slots today
#                     return []

#         slots = []
#         current_slot_start = start_of_day
#         while current_slot_start + timedelta(minutes=service.duration_minutes) <= end_of_day:
#             slot_end = current_slot_start + timedelta(minutes=service.duration_minutes)

#             # Check if this slot is available
#             overlapping_bookings_count = Booking.objects.filter(
#                 service=service,
#                 status__in=['pending', 'confirmed'],
#                 start_time__lt=slot_end,
#                 end_time__gt=current_slot_start
#             ).count()

#             if overlapping_bookings_count < service.max_bookings_per_slot:
#                 slots.append(current_slot_start)

#             current_slot_start += timedelta(minutes=service.duration_minutes) # Or a fixed interval like 30 minutes

#         return slots


# class UserBookingListView(LoginRequiredMixin, ListView):
#     model = Booking
#     template_name = 'bookings/user_bookings.html'
#     context_object_name = 'bookings'

#     def get_queryset(self):
#         return Booking.objects.filter(user=self.request.user).order_by('-start_time')

# class CancelBookingView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = Booking
#     template_name = 'bookings/cancel_booking.html'
#     success_url = reverse_lazy('bookings:user_bookings')

#     def test_func(self):
#         booking = self.get_object()
#         # Allow cancellation if user owns it and it's cancellable based on model property
#         return booking.user == self.request.user and booking.can_cancel

#     def get_object(self, queryset=None):
#         obj = super().get_object(queryset)
#         if not obj.can_cancel:
#             messages.error(self.request, "This booking cannot be cancelled at this time.")
#             # Redirect if they try to access cancellation page for non-cancellable booking
#             return redirect(self.success_url) # Or raise Http404, or use a specific error template
#         return obj

#     def form_valid(self, form):
#         booking = self.get_object()
#         booking.status = 'cancelled'
#         booking.save()
#         messages.info(self.request, f"Your booking for {booking.service.name} on {booking.start_time.strftime('%Y-%m-%d %H:%M')} has been cancelled.")
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         booking = self.get_object() # Ensure object is fetched to use in template
#         context['booking'] = booking
#         return context

# class BookingSuccessView(TemplateView):
#     template_name = 'bookings/booking_success.html'

# # --- User Profile Views ---
# class UserProfileView(LoginRequiredMixin, DetailView):
#     model = UserProfile
#     template_name = 'bookings/user_profile.html'
#     context_object_name = 'profile'

#     def get_object(self):
#         # Get or create UserProfile for the logged-in user
#         profile, created = UserProfile.objects.get_or_create(user=self.request.user)
#         return profile

# class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
#     model = UserProfile
#     form_class = UserProfileForm
#     template_name = 'bookings/user_profile_form.html'
#     success_url = reverse_lazy('bookings:user_profile')

#     def get_object(self):
#         # Get or create UserProfile for the logged-in user
#         profile, created = UserProfile.objects.get_or_create(user=self.request.user)
#         return profile

#     def form_valid(self, form):
#         messages.success(self.request, "Your profile has been updated successfully!")
#         return super().form_valid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, "There was an error updating your profile.")
#         return super().form_invalid(form)


# # --- AJAX View for Time Slots (Optional but good) ---
# def get_available_slots_ajax(request, service_id):
#     service = get_object_or_404(Service, pk=service_id)
#     selected_date_str = request.GET.get('date')

#     if not selected_date_str:
#         return JsonResponse({'error': 'Date parameter is required.'}, status=400)

#     try:
#         selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
#     except ValueError:
#         return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

#     slots = []
#     # Re-use the _generate_available_slots logic from BookServiceView
#     book_service_view_instance = BookServiceView()
#     book_service_view_instance.request = request # Set request for potential future use in _generate_available_slots
#     available_datetimes = book_service_view_instance._generate_available_slots(service, selected_date)

#     for dt in available_datetimes:
#         slots.append({
#             'datetime_iso': dt.isoformat(),
#             'time_display': dt.strftime('%H:%M'),
#         })

#     return JsonResponse({'slots': slots})

# from django.shortcuts import render, redirect, get_object_or_404
# from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView, View
# from django.urls import reverse_lazy, reverse
# from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib import messages
# from django.http import JsonResponse
# from django.utils import timezone
# from datetime import timedelta, datetime
# import calendar
# import json
# from django.db import models
# from .forms import BookingForm, ServiceSearchForm, UserProfileForm, TableForm, UserRegisterForm, StaffBookingFilterForm
# from .models import Service, Booking, UserProfile, Table
# from .utils import send_booking_confirmation_email
# from django.db.models import Count, Sum, Q
# from django import forms
# from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth import login, logout # Import login

# # --- User Registration ---
# class UserRegisterView(FormView):
#     template_name = 'registration/register.html'
#     form_class = UserCreationForm
#     success_url = reverse_lazy('login')

#     def form_valid(self, form):
#         form.save()
#         messages.success(self.request, "Registration successful. You may now log in.")
#         return super().form_valid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, "There was an error with your registration.")
#         return super().form_invalid(form)


# # --- Service Views ---
# class ServiceListView(ListView):
#     model = Service
#     template_name = 'bookings/service_list.html'
#     context_object_name = 'services'
#     paginate_by = 10

#     def get_queryset(self):
#         queryset = super().get_queryset().filter(is_available=True)
#         form = ServiceSearchForm(self.request.GET)
#         if form.is_valid():
#             query = form.cleaned_data.get('query')
#             if query:
#                 queryset = queryset.filter(name__icontains=query)
#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['search_form'] = ServiceSearchForm(self.request.GET)
#         return context


# class ServiceDetailView(DetailView):
#     model = Service
#     template_name = 'bookings/service_detail.html'
#     context_object_name = 'service'


# # --- Booking Views ---
# class BookServiceView(LoginRequiredMixin, CreateView):
#     model = Booking
#     form_class = BookingForm
#     template_name = 'bookings/book_service.html'
#     success_url = reverse_lazy('bookings:booking_success')

#     def get_initial(self):
#         initial = super().get_initial()
#         service = get_object_or_404(Service, pk=self.kwargs['pk'])
#         initial['service'] = service
#         return initial

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['service'] = get_object_or_404(Service, pk=self.kwargs['pk'])
#         return kwargs

#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         service = form.instance.service
#         start_time = form.cleaned_data['start_time']
#         end_time = start_time + timedelta(minutes=service.duration_minutes)
#         form.instance.end_time = end_time

#         if start_time < timezone.now():
#             form.add_error('start_time', "Cannot book a service in the past.")
#             return self.form_invalid(form)

#         overlapping_bookings_count = Booking.objects.filter(
#             service=service,
#             status__in=['pending', 'confirmed'],
#             start_time__lt=end_time,
#             end_time__gt=start_time
#         ).count()

#         if overlapping_bookings_count >= service.max_bookings_per_slot:
#             form.add_error(None, "This time slot is fully booked. Please choose another time.")
#             messages.error(self.request, "This time slot is fully booked. Please choose another time.")
#             return self.form_invalid(form)

#         response = super().form_valid(form)

#         send_booking_confirmation_email.delay(self.object.id)

#         messages.success(self.request, f"Your booking for {service.name} at {start_time.strftime('%Y-%m-%d %H:%M')} has been placed. A confirmation email will be sent.")
#         return response

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         service = get_object_or_404(Service, pk=self.kwargs['pk'])
#         context['service'] = service

#         today = timezone.localdate()
#         available_slots = []
#         for i in range(7):
#             day = today + timedelta(days=i)
#             slots_for_day = self._generate_available_slots(service, day)
#             if slots_for_day:
#                 available_slots.append({'date': day, 'slots': slots_for_day})

#         context['available_slots'] = available_slots
#         return context

#     def _generate_available_slots(self, service, date):
#         start_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time().replace(hour=9)))
#         end_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time().replace(hour=17)))

#         if date == timezone.localdate() and timezone.now() > start_of_day:
#             start_of_day = timezone.now().replace(minute=0, second=0, microsecond=0)
#             if start_of_day.hour >= 17:
#                 return []

#         slots = []
#         current_slot_start = start_of_day
#         while current_slot_start + timedelta(minutes=service.duration_minutes) <= end_of_day:
#             slot_end = current_slot_start + timedelta(minutes=service.duration_minutes)
#             overlapping_bookings_count = Booking.objects.filter(
#                 service=service,
#                 status__in=['pending', 'confirmed'],
#                 start_time__lt=slot_end,
#                 end_time__gt=current_slot_start
#             ).count()
#             if overlapping_bookings_count < service.max_bookings_per_slot:
#                 slots.append(current_slot_start)
#             current_slot_start += timedelta(minutes=service.duration_minutes)

#         return slots


# class UserBookingListView(LoginRequiredMixin, ListView):
#     model = Booking
#     template_name = 'bookings/user_bookings.html'
#     context_object_name = 'bookings'

#     def get_queryset(self):
#         return Booking.objects.filter(user=self.request.user).order_by('-start_time')


# class CancelBookingView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = Booking
#     template_name = 'bookings/cancel_booking.html'
#     success_url = reverse_lazy('bookings:user_bookings')

#     def test_func(self):
#         booking = self.get_object()
#         return booking.user == self.request.user and booking.can_cancel

#     def get_object(self, queryset=None):
#         obj = super().get_object(queryset)
#         if not obj.can_cancel:
#             messages.error(self.request, "This booking cannot be cancelled.")
#             return redirect(self.success_url)
#         return obj

#     def form_valid(self, form):
#         booking = self.get_object()
#         booking.status = 'cancelled'
#         booking.save()
#         messages.info(self.request, f"Your booking for {booking.service.name} on {booking.start_time.strftime('%Y-%m-%d %H:%M')} has been cancelled.")
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['booking'] = self.get_object()
#         return context


# class BookingSuccessView(TemplateView):
#     template_name = 'bookings/booking_success.html'


# # --- User Profile Views ---
# class UserProfileView(LoginRequiredMixin, DetailView):
#     model = UserProfile
#     template_name = 'bookings/user_profile.html'
#     context_object_name = 'profile'

#     def get_object(self):
#         profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
#         return profile


# class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
#     model = UserProfile
#     form_class = UserProfileForm
#     template_name = 'bookings/user_profile_form.html'
#     success_url = reverse_lazy('bookings:user_profile')

#     def get_object(self):
#         profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
#         return profile

#     def form_valid(self, form):
#         messages.success(self.request, "Your profile has been updated successfully!")
#         return super().form_valid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, "There was an error updating your profile.")
#         return super().form_invalid(form)


# # --- AJAX for Time Slot Loading ---
# def get_available_slots_ajax(request, service_id):
#     service = get_object_or_404(Service, pk=service_id)
#     selected_date_str = request.GET.get('date')

#     if not selected_date_str:
#         return JsonResponse({'error': 'Date parameter is required.'}, status=400)

#     try:
#         selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
#     except ValueError:
#         return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

#     view = BookServiceView()
#     view.request = request
#     available_datetimes = view._generate_available_slots(service, selected_date)

#     slots = [{
#         'datetime_iso': dt.isoformat(),
#         'time_display': dt.strftime('%H:%M')
#     } for dt in available_datetimes]

#     return JsonResponse({'slots': slots})


# # --- Register function-based alias for class-based view ---
# register = UserRegisterView.as_view()


# # --- Mixin for Staff Access ---
# class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
#     def test_func(self):
#         return self.request.user.is_staff

#     def handle_no_permission(self):
#         messages.error(self.request, "You do not have permission to access this page.")
#         return redirect('login') # Or your desired unauthorized page/URL

# # --- Staff Dashboard Views ---
# class StaffDashboardView(StaffRequiredMixin, TemplateView):
#     template_name = 'bookings/staff/dashboard.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Add summary data for the dashboard
#         context['total_tables'] = Table.objects.count()
#         context['available_tables'] = Table.objects.filter(is_available=True).count()
#         context['total_bookings'] = Booking.objects.count()
#         context['pending_bookings'] = Booking.objects.filter(status='pending').count()
#         context['confirmed_bookings'] = Booking.objects.filter(status='confirmed', end_time__gte=timezone.now()).count()
#         context['upcoming_bookings'] = Booking.objects.filter(
#             start_time__gte=timezone.now(),
#             status__in=['pending', 'confirmed']
#         ).order_by('start_time')[:10] # Show next 10 upcoming
#         return context

# class TableListView(StaffRequiredMixin, ListView):
#     model = Table
#     template_name = 'bookings/staff/table_list.html'
#     context_object_name = 'tables'
#     ordering = ['name']

# class TableDetailView(StaffRequiredMixin, DetailView):
#     model = Table
#     template_name = 'bookings/staff/table_detail.html'
#     context_object_name = 'table'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         table = self.get_object()
#         # Get bookings for this specific table (for current/upcoming)
#         context['current_bookings'] = Booking.objects.filter(
#             table=table,
#             start_time__lte=timezone.now(),
#             end_time__gte=timezone.now(),
#             status__in=['pending', 'confirmed']
#         ).order_by('start_time')
#         context['upcoming_bookings'] = Booking.objects.filter(
#             table=table,
#             start_time__gt=timezone.now(),
#             status__in=['pending', 'confirmed']
#         ).order_by('start_time')[:10]
#         return context

# class TableCreateView(StaffRequiredMixin, CreateView):
#     model = Table
#     form_class = TableForm
#     template_name = 'bookings/staff/table_form.html'
#     success_url = reverse_lazy('bookings:staff_table_list')

#     def form_valid(self, form):
#         messages.success(self.request, f"Table '{form.instance.name}' created successfully!")
#         return super().form_valid(form)

# class TableUpdateView(StaffRequiredMixin, UpdateView):
#     model = Table
#     form_class = TableForm
#     template_name = 'bookings/staff/table_form.html'
#     success_url = reverse_lazy('bookings:staff_table_list')

#     def form_valid(self, form):
#         messages.success(self.request, f"Table '{form.instance.name}' updated successfully!")
#         return super().form_valid(form)

# class TableDeleteView(StaffRequiredMixin, DeleteView):
#     model = Table
#     template_name = 'bookings/staff/table_confirm_delete.html'
#     success_url = reverse_lazy('bookings:staff_table_list')

#     def form_valid(self, form):
#         messages.success(self.request, f"Table '{self.object.name}' deleted successfully!")
#         return super().form_valid(form)

# # --- Booking Management (for Staff) ---
# class StaffBookingListView(StaffRequiredMixin, ListView):
#     model = Booking
#     template_name = 'bookings/staff/booking_list.html'
#     context_object_name = 'bookings'
#     paginate_by = 20 # Add pagination for staff view

#     def get_queryset(self):
#         # Order by start_time, then status to show pending first
#         queryset = super().get_queryset().order_by('-start_time')
#         # You could add filtering options here (e.g., by date, by status)
#         return queryset

# class StaffBookingDetailView(StaffRequiredMixin, DetailView):
#     model = Booking
#     template_name = 'bookings/staff/booking_detail.html'
#     context_object_name = 'booking'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # You might add options to change status from here
#         return context

# # --- Action to confirm/cancel booking from staff side (new) ---
# class StaffBookingActionView(StaffRequiredMixin, UpdateView):
#     model = Booking
#     fields = ['status'] # Only allow changing status here
#     template_name = 'bookings/staff/booking_action_confirm.html' # A simple confirmation page
#     # success_url is handled dynamically

#     def get_success_url(self):
#         return reverse_lazy('bookings:staff_booking_detail', kwargs={'pk': self.object.pk})

#     def form_valid(self, form):
#         old_status = self.get_object().status
#         new_status = form.cleaned_data['status']
#         response = super().form_valid(form)
#         if new_status != old_status:
#             messages.success(self.request, f"Booking status for {self.object} changed from '{old_status}' to '{new_status}'.")
#             # You might want to send email notifications for status changes
#             # For example, if status changes to 'confirmed' or 'cancelled'
#         return response

#     def get(self, request, *args, **kwargs):
#         # This allows direct POST requests for quick actions without a separate form page
#         if request.GET.get('action') == 'confirm':
#             booking = self.get_object()
#             if booking.status == 'pending':
#                 booking.status = 'confirmed'
#                 booking.save()
#                 messages.success(request, f"Booking {booking.id} confirmed.")
#                 return redirect(self.get_success_url())
#             else:
#                 messages.error(request, f"Booking {booking.id} cannot be confirmed from its current status.")
#                 return redirect(self.get_success_url())
#         elif request.GET.get('action') == 'cancel':
#             booking = self.get_object()
#             if booking.status != 'cancelled': # Prevent re-cancelling
#                 booking.status = 'cancelled'
#                 booking.save()
#                 messages.info(request, f"Booking {booking.id} cancelled.")
#                 return redirect(self.get_success_url())
#             else:
#                 messages.error(request, f"Booking {booking.id} is already cancelled.")
#                 return redirect(self.get_success_url())

#         # If not a quick action, render the form normally
#         return super().get(request, *args, **kwargs)


# # --- Mixin for Staff Access ---
# class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
#     def test_func(self):
#         return self.request.user.is_staff and self.request.user.is_active

#     def handle_no_permission(self):
#         messages.error(self.request, "You do not have permission to access this page.")
#         return redirect('login') # Redirect to login if not authenticated or not staff

# # --- Staff Dashboard Views ---
# class StaffDashboardView(StaffRequiredMixin, TemplateView):
#     template_name = 'bookings/staff/dashboard.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         # General Summary
#         context['total_tables'] = Table.objects.count()
#         context['available_tables'] = Table.objects.filter(is_available=True).count()
#         context['total_bookings'] = Booking.objects.count()
#         context['pending_bookings'] = Booking.objects.filter(status='pending').count()
#         context['confirmed_bookings'] = Booking.objects.filter(status='confirmed', end_time__gte=timezone.now()).count()

#         # Upcoming Bookings (Top N, e.g., 10)
#         context['upcoming_bookings'] = Booking.objects.filter(
#             start_time__gte=timezone.now(),
#             status__in=['pending', 'confirmed']
#         ).order_by('start_time')[:10].select_related('user', 'service', 'table') # Optimize query

#         # --- Analytics Data for Charts ---
#         # 1. Bookings per month (last 6 months, confirmed only)
#         six_months_ago = timezone.now() - timedelta(days=180) # Approximately 6 months
#         monthly_bookings_data = Booking.objects.filter(
#             created_at__gte=six_months_ago,
#             status='confirmed' # Only confirmed bookings for analytics
#         ).extra({'month_year': "strftime('%%Y-%%m', created_at)"}).values('month_year').annotate(
#             count=Count('id')
#         ).order_by('month_year')

#         monthly_labels = [m['month_year'] for m in monthly_bookings_data]
#         monthly_counts = [m['count'] for m in monthly_bookings_data]
#         context['monthly_bookings_labels'] = json.dumps(monthly_labels)
#         context['monthly_bookings_data'] = json.dumps(monthly_counts)

#         # 2. Service Popularity (Top 5 most booked confirmed services)
#         service_popularity_data = Service.objects.annotate(
#             booking_count=Count('booking', filter=models.Q(booking__status='confirmed'))
#         ).order_by('-booking_count')[:5].values('name', 'booking_count')

#         service_labels = [s['name'] for s in service_popularity_data]
#         service_counts = [s['booking_count'] for s in service_popularity_data]
#         context['service_popularity_labels'] = json.dumps(service_labels)
#         context['service_popularity_data'] = json.dumps(service_counts)

#         # 3. Revenue over last 6 months (sum of service prices for confirmed bookings)
#         monthly_revenue_data = Booking.objects.filter(
#             status='confirmed',
#             created_at__gte=six_months_ago
#         ).extra({'month_year': "strftime('%%Y-%%m', created_at)"}).values('month_year').annotate(
#             total_revenue=Sum('service__price')
#         ).order_by('month_year')

#         monthly_revenue_labels = [m['month_year'] for m in monthly_revenue_data]
#         # Ensure total_revenue is a float or 0 if None
#         monthly_revenue_values = [float(m['total_revenue']) if m['total_revenue'] else 0 for m in monthly_revenue_data]
#         context['monthly_revenue_labels'] = json.dumps(monthly_revenue_labels)
#         context['monthly_revenue_data'] = json.dumps(monthly_revenue_values)

#         return context

# # --- Table Management Views (Keep as is) ---
# # TableListView, TableDetailView, TableCreateView, TableUpdateView, TableDeleteView

# # --- Booking Management (for Staff) ---
# class StaffBookingListView(StaffRequiredMixin, ListView):
#     model = Booking
#     template_name = 'bookings/staff/booking_list.html'
#     context_object_name = 'bookings'
#     paginate_by = 20

#     def get_queryset(self):
#         # Initial queryset, then apply filters
#         queryset = Booking.objects.all().order_by('-start_time').select_related('user', 'service', 'table')
#         self.filter = StaffBookingFilterForm(self.request.GET, queryset=queryset)
#         return self.filter.qs # Returns the filtered queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['filter_form'] = self.filter.form # Pass the form to the template
#         return context

# # bookings/views.py - inside StaffBookingDetailView
# class StaffBookingDetailView(StaffRequiredMixin, DetailView):
#     model = Booking
#     template_name = 'bookings/staff/booking_detail.html'
#     context_object_name = 'booking'
#     queryset = Booking.objects.select_related('user', 'service', 'table')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['all_tables'] = Table.objects.all().order_by('name') # Pass all tables for assignment dropdown
#         return context

# class StaffBookingActionView(StaffRequiredMixin, View): # Change to simple View for direct actions
#     def post(self, request, pk, *args, **kwargs): # Use POST for actions
#         booking = get_object_or_404(Booking, pk=pk)
#         action = request.POST.get('action') # Get action from POST data

#         if action == 'confirm' and booking.status == 'pending':
#             booking.status = 'confirmed'
#             booking.save()
#             messages.success(request, f"Booking {booking.id} confirmed.")
#         elif action == 'cancel' and booking.status != 'cancelled':
#             booking.status = 'cancelled'
#             booking.save()
#             messages.info(request, f"Booking {booking.id} cancelled.")
#         elif action == 'assign_table':
#             table_id = request.POST.get('table_id')
#             if table_id:
#                 try:
#                     table = Table.objects.get(pk=table_id)
#                     booking.table = table
#                     booking.save()
#                     messages.success(request, f"Table {table.name} assigned to Booking {booking.id}.")
#                 except Table.DoesNotExist:
#                     messages.error(request, "Selected table does not exist.")
#             else:
#                 messages.error(request, "No table selected for assignment.")
#         else:
#             messages.error(request, f"Invalid action '{action}' or action not applicable for current booking status '{booking.status}'.")

#         return redirect(reverse('bookings:staff_booking_detail', kwargs={'pk': booking.pk}))

#     # If you still want to offer a form to change status/table,
#     # you'd keep the UpdateView and have a separate form for it.
#     # For now, we're simplifying with direct POST actions.

# # --- Calendar Views for Staff ---
# class BookingCalendarView(StaffRequiredMixin, TemplateView):
#     template_name = 'bookings/staff/calendar.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Default calendar settings for FullCalendar.js
#         context['calendar_settings'] = {
#             'initialView': 'timeGridWeek', # Default view
#             'slotMinTime': "09:00:00", # Example: Start time for slots
#             'slotMaxTime': "18:00:00", # Example: End time for slots
#             'firstDay': 1, # Monday
#             'nowIndicator': True, # Show current time
#             'weekends': True, # Show weekends
#             'editable': False, # Don't allow drag-and-drop editing from calendar
#             'dayMaxEvents': True, # Allow "more" link when too many events
#             'headerToolbar': {
#                 'left': 'prev,next today',
#                 'center': 'title',
#                 'right': 'dayGridMonth,timeGridWeek,timeGridDay' # Views available
#             }
#         }
#         return context

# class BookingCalendarAPIView(StaffRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         start_str = request.GET.get('start')
#         end_str = request.GET.get('end')

#         if not start_str or not end_str:
#             return JsonResponse({'error': 'Start and end dates are required.'}, status=400)

#         # FullCalendar sends ISO 8601 strings, which Django can parse
#         # Handle potential timezone 'Z' for UTC if fromisoformat can't handle it directly
#         # Ensure dates are timezone-aware using Django's timezone
#         try:
#             start_date = timezone.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
#             end_date = timezone.datetime.fromisoformat(end_str.replace('Z', '+00:00'))
#         except ValueError:
#             return JsonResponse({'error': 'Invalid date format. Use ISO 8601.'}, status=400)

#         # Make dates timezone-aware if they are naive (FullCalendar usually sends aware)
#         if timezone.is_naive(start_date):
#             start_date = timezone.make_aware(start_date)
#         if timezone.is_naive(end_date):
#             end_date = timezone.make_aware(end_date)

#         # Fetch bookings within the requested date range
#         bookings = Booking.objects.filter(
#             start_time__gte=start_date,
#             end_time__lte=end_date,
#             status__in=['pending', 'confirmed'] # Only show relevant statuses
#         ).select_related('service', 'user', 'table') # Optimize database queries

#         events = []
#         for booking in bookings:
#             event_color = '#3498db' # Default blue for confirmed
#             if booking.status == 'pending':
#                 event_color = '#f39c12' # Orange for pending
#             elif booking.status == 'cancelled': # Though we filter out cancelled, good to have
#                 event_color = '#e74c3c' # Red for cancelled

#             title = f"{booking.user.username} - {booking.service.name}"
#             if booking.table:
#                 title += f" (Table: {booking.table.name})"

#             events.append({
#                 'id': booking.id,
#                 'title': title,
#                 'start': booking.start_time.isoformat(), # ISO 8601 format for FullCalendar
#                 'end': booking.end_time.isoformat(),
#                 'url': reverse('bookings:staff_booking_detail', args=[booking.id]), # Link to staff detail page
#                 'backgroundColor': event_color,
#                 'borderColor': event_color,
#                 'status': booking.status, # Custom property for JS access
#             })
#         return JsonResponse(events, safe=False) # safe=False is needed for list of dictionaries

# # --- Existing Customer-facing Views (No changes) ---
# # ServiceListView, ServiceDetailView, BookServiceView, UserBookingListView, CancelBookingView, BookingSuccessView, UserProfileView, UserProfileUpdateView, UserRegisterView, get_available_slots_ajax


from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView, View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse # Added HttpResponse for potential PDF response
from django.utils import timezone
from datetime import timedelta, datetime, date
import calendar
import json
from django.db import models
from django.db.models import Count, Sum, Q # Ensure Q is imported for complex queries
from django.contrib.auth import login, logout # Import login, logout for direct use

# Import your forms - CRUCIAL TO HAVE USERREGISTERFORM HERE
from .forms import (
    BookingForm,
    ServiceSearchForm,
    UserProfileForm,
    TableForm,
    UserRegisterForm, # <--- VERIFIED: This is correctly imported
    StaffBookingFilterForm
)

# Import your models
from .models import Service, Booking, UserProfile, Table # Ensure all necessary models are imported

# Import your utility functions
from .utils import send_booking_confirmation_email, generate_booking_confirmation_pdf # Make sure you have generate_booking_confirmation_pdf if used

# --- Mixin for Staff Access ---
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        # User must be authenticated and be staff
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access this page. Please log in with a staff account.")
        return redirect('login') # Redirect to login if not authenticated or not staff

# --- User Registration ---
class UserRegisterView(CreateView): # <--- CRITICAL CHANGE: Using CreateView for model creation
    form_class = UserRegisterForm # <--- CRITICAL CHANGE: Using YOUR custom UserRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('bookings:service_list') # Redirect to service list after successful login

    def form_valid(self, form):
        # CreateView automatically saves the form instance to self.object
        response = super().form_valid(form) # This calls form.save() for you
        
        # Log the user in immediately after successful registration
        login(self.request, self.object) # self.object is the newly created User instance
        messages.success(self.request, 'Your account has been created and you are now logged in!')
        return response # This will now follow the success_url

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your registration. Please correct the errors below.')
        return super().form_invalid(form)

# --- Service Views ---
class ServiceListView(ListView):
    model = Service
    template_name = 'bookings/service_list.html'
    context_object_name = 'services'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_available=True)
        form = ServiceSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            if query:
                queryset = queryset.filter(name__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ServiceSearchForm(self.request.GET)
        return context


class ServiceDetailView(DetailView):
    model = Service
    template_name = 'bookings/service_detail.html'
    context_object_name = 'service'


# --- Booking Views ---
class BookServiceView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/book_service.html'
    success_url = reverse_lazy('bookings:booking_success')

    def get_initial(self):
        initial = super().get_initial()
        service = get_object_or_404(Service, pk=self.kwargs['pk'])
        initial['service'] = service
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['service'] = get_object_or_404(Service, pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        service = form.instance.service
        start_time = form.cleaned_data['start_time']
        end_time = start_time + timedelta(minutes=service.duration_minutes)
        form.instance.end_time = end_time

        # Time validation is also done in BookingForm clean_start_time, but this is a double check
        if start_time < timezone.now():
            form.add_error('start_time', "Cannot book a service in the past.")
            return self.form_invalid(form)

        # Logic for max_bookings_per_slot (also handled in BookingForm clean method)
        overlapping_bookings_count = Booking.objects.filter(
            service=service,
            status__in=['pending', 'confirmed'],
            start_time__lt=end_time,
            end_time__gt=start_time
        ).count()

        if overlapping_bookings_count >= service.max_bookings_per_slot:
            form.add_error(None, "This time slot is fully booked. Please choose another time.")
            messages.error(self.request, "This time slot is fully booked. Please choose another time.")
            return self.form_invalid(form)

        response = super().form_valid(form) # Saves the booking instance

        # Asynchronous email sending
        send_booking_confirmation_email.delay(self.object.id)

        messages.success(self.request, f"Your booking for {service.name} at {start_time.strftime('%Y-%m-%d %H:%M')} has been placed. A confirmation email will be sent.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = get_object_or_404(Service, pk=self.kwargs['pk'])
        context['service'] = service

        today = timezone.localdate()
        available_slots = []
        for i in range(7): # Generate slots for the next 7 days
            day = today + timedelta(days=i)
            slots_for_day = self._generate_available_slots(service, day)
            if slots_for_day:
                available_slots.append({'date': day, 'slots': slots_for_day})

        context['available_slots'] = available_slots
        return context

    def _generate_available_slots(self, service, date):
        # Business hours example: 9 AM to 5 PM
        start_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time().replace(hour=9, minute=0, second=0)))
        end_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time().replace(hour=17, minute=0, second=0)))

        # Adjust start_of_day if it's today and current time is past 9 AM
        if date == timezone.localdate():
            now = timezone.now()
            if now > start_of_day:
                # Round up to the nearest interval if current time is not an exact interval start
                current_slot_candidate = now.replace(minute=(now.minute // service.duration_minutes) * service.duration_minutes, second=0, microsecond=0)
                if now.minute % service.duration_minutes != 0:
                    current_slot_candidate += timedelta(minutes=service.duration_minutes - (now.minute % service.duration_minutes))
                
                if current_slot_candidate > start_of_day:
                    start_of_day = current_slot_candidate

            if start_of_day >= end_of_day: # No more slots left today
                return []

        slots = []
        current_slot_start = start_of_day
        while current_slot_start + timedelta(minutes=service.duration_minutes) <= end_of_day:
            slot_end = current_slot_start + timedelta(minutes=service.duration_minutes)
            
            # Count current confirmed/pending bookings for this service and slot
            overlapping_bookings_count = Booking.objects.filter(
                service=service,
                status__in=['pending', 'confirmed'],
                start_time__lt=slot_end, # Booking starts before this slot ends
                end_time__gt=current_slot_start # Booking ends after this slot starts
            ).count()

            if overlapping_bookings_count < service.max_bookings_per_slot:
                slots.append(current_slot_start)
            current_slot_start += timedelta(minutes=service.duration_minutes)

        return slots


class UserBookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/user_bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        # Fetch user's bookings and optimize with select_related
        return Booking.objects.filter(user=self.request.user).order_by('-start_time').select_related('service')


class CancelBookingView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Booking
    template_name = 'bookings/cancel_booking.html'
    success_url = reverse_lazy('bookings:user_bookings')

    def test_func(self):
        booking = self.get_object()
        # Ensure user owns the booking and it can be cancelled based on its method
        return booking.user == self.request.user and booking.can_cancel() # Assuming can_cancel is a method

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.can_cancel(): # Re-check before allowing access to confirm page
            messages.error(self.request, "This booking cannot be cancelled at this time.")
            return redirect(self.success_url)
        return obj

    def form_valid(self, form):
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.save()
        messages.info(self.request, f"Your booking for {booking.service.name} on {booking.start_time.strftime('%Y-%m-%d %H:%M')} has been cancelled.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking'] = self.get_object()
        return context


class BookingSuccessView(TemplateView):
    template_name = 'bookings/booking_success.html'


# --- User Profile Views ---
class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'bookings/user_profile.html'
    context_object_name = 'profile'

    def get_object(self):
        # Get or create UserProfile for the current user
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'bookings/user_profile_form.html'
    success_url = reverse_lazy('bookings:user_profile')

    def get_object(self):
        # Get or create UserProfile for the current user to update
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error updating your profile.")
        return super().form_invalid(form)


# --- AJAX for Time Slot Loading ---
def get_available_slots_ajax(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    selected_date_str = request.GET.get('date')

    if not selected_date_str:
        return JsonResponse({'error': 'Date parameter is required.'}, status=400)

    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    # Instantiate the view to reuse its _generate_available_slots logic
    view = BookServiceView()
    view.request = request # Pass the request object
    available_datetimes = view._generate_available_slots(service, selected_date)

    slots = [{
        'datetime_iso': dt.isoformat(),
        'time_display': dt.strftime('%H:%M')
    } for dt in available_datetimes]

    return JsonResponse({'slots': slots})


# --- Staff Dashboard Views ---
class StaffDashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'bookings/staff/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add summary data for the dashboard
        context['total_tables'] = Table.objects.count()
        context['available_tables'] = Table.objects.filter(is_available=True).count()
        context['total_bookings'] = Booking.objects.count()
        context['pending_bookings'] = Booking.objects.filter(status='pending').count()
        context['confirmed_bookings'] = Booking.objects.filter(status='confirmed', end_time__gte=timezone.now()).count()
        context['upcoming_bookings'] = Booking.objects.filter(
            start_time__gte=timezone.now(),
            status__in=['pending', 'confirmed']
        ).order_by('start_time')[:10].select_related('user', 'service', 'table') # Optimize query
        
        # --- Analytics Data for Charts ---
        # 1. Bookings per month (last 6 months, confirmed only)
        # Ensure timezone.now() is correctly offset for the start of the period
        six_months_ago = timezone.now() - timedelta(days=180) # Approximately 6 months
        
        # For SQLite (default Django dev DB), strftime is used. For PostgreSQL, use TruncMonth.
        # This example assumes SQLite-like behavior for simplicity in snippet.
        # If using PostgreSQL, consider: from django.db.models.functions import TruncMonth
        # .annotate(month_year=TruncMonth('created_at', tzinfo=timezone.get_current_timezone()))
        
        monthly_bookings_data = Booking.objects.filter(
            created_at__gte=six_months_ago,
            status='confirmed' # Only confirmed bookings for analytics
        ).extra({'month_year': "strftime('%%Y-%%m', created_at)"}).values('month_year').annotate(
            count=Count('id')
        ).order_by('month_year')

        monthly_labels = [m['month_year'] for m in monthly_bookings_data]
        monthly_counts = [m['count'] for m in monthly_bookings_data]
        context['monthly_bookings_labels'] = json.dumps(monthly_labels)
        context['monthly_bookings_data'] = json.dumps(monthly_counts)

        # 2. Service Popularity (Top 5 most booked confirmed services)
        service_popularity_data = Service.objects.annotate(
            booking_count=Count('booking', filter=models.Q(booking__status='confirmed'))
        ).order_by('-booking_count')[:5].values('name', 'booking_count')

        service_labels = [s['name'] for s in service_popularity_data]
        service_counts = [s['booking_count'] for s in service_popularity_data]
        context['service_popularity_labels'] = json.dumps(service_labels)
        context['service_popularity_data'] = json.dumps(service_counts)

        # 3. Revenue over last 6 months (sum of service prices for confirmed bookings)
        monthly_revenue_data = Booking.objects.filter(
            status='confirmed',
            created_at__gte=six_months_ago
        ).extra({'month_year': "strftime('%%Y-%%m', created_at)"}).values('month_year').annotate(
            total_revenue=Sum('service__price')
        ).order_by('month_year')

        monthly_revenue_labels = [m['month_year'] for m in monthly_revenue_data]
        # Ensure total_revenue is a float or 0 if None
        monthly_revenue_values = [float(m['total_revenue']) if m['total_revenue'] else 0 for m in monthly_revenue_data]
        context['monthly_revenue_labels'] = json.dumps(monthly_revenue_labels)
        context['monthly_revenue_data'] = json.dumps(monthly_revenue_values)

        return context

# --- Table Management Views (Staff) ---
class TableListView(StaffRequiredMixin, ListView):
    model = Table
    template_name = 'bookings/staff/table_list.html'
    context_object_name = 'tables'
    ordering = ['name']

class TableDetailView(StaffRequiredMixin, DetailView):
    model = Table
    template_name = 'bookings/staff/table_detail.html'
    context_object_name = 'table'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.get_object()
        # Get bookings for this specific table (for current/upcoming)
        context['current_bookings'] = Booking.objects.filter(
            table=table,
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now(),
            status__in=['pending', 'confirmed']
        ).order_by('start_time').select_related('user', 'service')
        
        context['upcoming_bookings'] = Booking.objects.filter(
            table=table,
            start_time__gt=timezone.now(),
            status__in=['pending', 'confirmed']
        ).order_by('start_time')[:10].select_related('user', 'service')
        return context

class TableCreateView(StaffRequiredMixin, CreateView):
    model = Table
    form_class = TableForm
    template_name = 'bookings/staff/table_form.html'
    success_url = reverse_lazy('bookings:staff_table_list')

    def form_valid(self, form):
        messages.success(self.request, f"Table '{form.instance.name}' created successfully!")
        return super().form_valid(form)

class TableUpdateView(StaffRequiredMixin, UpdateView):
    model = Table
    form_class = TableForm
    template_name = 'bookings/staff/table_form.html'
    success_url = reverse_lazy('bookings:staff_table_list')

    def form_valid(self, form):
        messages.success(self.request, f"Table '{form.instance.name}' updated successfully!")
        return super().form_valid(form)

class TableDeleteView(StaffRequiredMixin, DeleteView):
    model = Table
    template_name = 'bookings/staff/table_confirm_delete.html'
    success_url = reverse_lazy('bookings:staff_table_list')

    def form_valid(self, form):
        messages.success(self.request, f"Table '{self.object.name}' deleted successfully!")
        return super().form_valid(form)

# --- Booking Management (for Staff) ---
class StaffBookingListView(StaffRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/staff/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        # Initial queryset, then apply filters. Optimized with select_related
        queryset = Booking.objects.all().order_by('-start_time').select_related('user', 'service', 'table')
        self.filter = StaffBookingFilterForm(self.request.GET, queryset=queryset)
        return self.filter.qs # Returns the filtered queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.filter.form # Pass the form to the template
        return context

class StaffBookingDetailView(StaffRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/staff/booking_detail.html'
    context_object_name = 'booking'
    queryset = Booking.objects.select_related('user', 'service', 'table') # Optimize initial query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_tables'] = Table.objects.all().order_by('name') # Pass all tables for assignment dropdown
        return context

class StaffBookingActionView(StaffRequiredMixin, View): # Using View for direct POST actions
    def post(self, request, pk, *args, **kwargs): # Use POST for actions
        booking = get_object_or_404(Booking, pk=pk)
        action = request.POST.get('action') # Get action from POST data

        if action == 'confirm' and booking.status == 'pending':
            booking.status = 'confirmed'
            booking.save()
            messages.success(request, f"Booking {booking.id} confirmed.")
        elif action == 'cancel' and booking.status != 'cancelled':
            booking.status = 'cancelled'
            booking.save()
            messages.info(request, f"Booking {booking.id} cancelled.")
        elif action == 'assign_table':
            table_id = request.POST.get('table_id')
            if table_id:
                try:
                    table = Table.objects.get(pk=table_id)
                    booking.table = table
                    booking.save()
                    messages.success(request, f"Table {table.name} assigned to Booking {booking.id}.")
                except Table.DoesNotExist:
                    messages.error(request, "Selected table does not exist.")
            else:
                messages.error(request, "No table selected for assignment.")
        else:
            messages.error(request, f"Invalid action '{action}' or action not applicable for current booking status '{booking.status}'.")

        return redirect(reverse('bookings:staff_booking_detail', kwargs={'pk': booking.pk}))

# --- Calendar Views for Staff ---
class BookingCalendarView(StaffRequiredMixin, TemplateView):
    template_name = 'bookings/staff/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Default calendar settings for FullCalendar.js
        context['calendar_settings'] = {
            'initialView': 'timeGridWeek', # Default view
            'slotMinTime': "09:00:00", # Example: Start time for slots
            'slotMaxTime': "18:00:00", # Example: End time for slots
            'firstDay': 1, # Monday
            'nowIndicator': True, # Show current time
            'weekends': True, # Show weekends
            'editable': False, # Don't allow drag-and-drop editing from calendar
            'dayMaxEvents': True, # Allow "more" link when too many events
            'headerToolbar': {
                'left': 'prev,next today',
                'center': 'title',
                'right': 'dayGridMonth,timeGridWeek,timeGridDay' # Views available
            }
        }
        return context

class BookingCalendarAPIView(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        start_str = request.GET.get('start')
        end_str = request.GET.get('end')

        if not start_str or not end_str:
            return JsonResponse({'error': 'Start and end dates are required.'}, status=400)

        try:
            start_date = timezone.datetime.fromisoformat(start_str.replace('Z', '+00:00')) # Handle 'Z' for UTC
            end_date = timezone.datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use ISO 8601.'}, status=400)

        # Ensure dates are timezone-aware if they are naive (FullCalendar usually sends aware)
        if timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date)
        if timezone.is_naive(end_date):
            end_date = timezone.make_aware(end_date)

        # Fetch bookings within the requested date range, optimized
        bookings = Booking.objects.filter(
            start_time__gte=start_date,
            end_time__lte=end_date,
            status__in=['pending', 'confirmed'] # Only show relevant statuses
        ).select_related('service', 'user', 'table') # Optimize database queries

        events = []
        for booking in bookings:
            event_color = '#3498db' # Default blue for confirmed
            if booking.status == 'pending':
                event_color = '#f39c12' # Orange for pending
            elif booking.status == 'cancelled': # Though we filter out cancelled, good to have
                event_color = '#e74c3c' # Red for cancelled

            title = f"{booking.user.username} - {booking.service.name}"
            if booking.table:
                title += f" (Table: {booking.table.name})"

            events.append({
                'id': booking.id,
                'title': title,
                'start': booking.start_time.isoformat(), # ISO 8601 format for FullCalendar
                'end': booking.end_time.isoformat(),
                'url': reverse('bookings:staff_booking_detail', args=[booking.id]), # Link to staff detail page
                'backgroundColor': event_color,
                'borderColor': event_color,
                'status': booking.status, # Custom property for JS access
            })
        return JsonResponse(events, safe=False) # safe=False is needed for list of dictionaries