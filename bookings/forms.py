# bookings/forms.py
from django import forms
from .models import Booking, UserProfile, Table, Service
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import timedelta
import django_filters

class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

class BookingForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=DateTimeInput,
        help_text="Please select a date and time for your booking."
    )

    class Meta:
        model = Booking
        fields = ['service', 'start_time']

    def __init__(self, *args, **kwargs):
        service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)

        if service:
            self.fields['service'].initial = service.id
            self.fields['service'].widget = forms.HiddenInput()

        self.fields['start_time'].widget.attrs['min'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        if start_time and start_time < timezone.now():
            raise forms.ValidationError("Booking cannot be in the past.")
        return start_time

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        start_time = cleaned_data.get('start_time')

        if not service or not start_time:
            return cleaned_data

        overlapping = Booking.objects.filter(
            service=service,
            start_time=start_time,
            status__in=['pending', 'confirmed']
        )

        if overlapping.exists():
            raise forms.ValidationError("This time slot is fully booked. Please choose another time.")

        return cleaned_data


class ServiceSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        label='Search Services',
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Massage, Consultation'})
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address']


class UserRegisterForm(UserCreationForm):
    # Explicitly define all additional fields you want on the registration form
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=150, required=False, help_text='Optional.') # Added first_name
    last_name = forms.CharField(max_length=150, required=False, help_text='Optional.')   # Added last_name
    phone_number = forms.CharField(max_length=20, required=False, help_text="Optional phone number")
    address = forms.CharField(widget=forms.Textarea, required=False, help_text="Optional address")

    class Meta(UserCreationForm.Meta):
        model = User
        # IMPORTANT: Include ALL fields you want to appear on the form here
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'phone_number', 'address',)
    
    def clean_email(self):
        email = self.cleaned_data['email']
        # Use iexact for case-insensitive email check
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            # Create a UserProfile for the new user, passing phone_number and address
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number'),
                address=self.cleaned_data.get('address')
            )
        return user


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['name', 'capacity', 'is_available', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }


class StaffBookingFilterForm(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='start_time', lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Bookings From'
    )
    end_date = django_filters.DateFilter(
        field_name='start_time', lookup_expr='lte',
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Bookings To'
    )
    status = django_filters.ChoiceFilter(
        choices=Booking.STATUS_CHOICES,
        empty_label="Any Status",
        label='Status'
    )
    service = django_filters.ModelChoiceFilter(
        queryset=Service.objects.all().order_by('name'),
        empty_label="Any Service",
        label='Service'
    )
    table = django_filters.ModelChoiceFilter(
        queryset=Table.objects.all().order_by('name'),
        empty_label="Any Table",
        label='Table'
    )
    user_username = django_filters.CharFilter(
        field_name='user__username', lookup_expr='icontains',
        label='User Username Contains'
    )
    user_email = django_filters.CharFilter(
        field_name='user__email', lookup_expr='icontains',
        label='User Email Contains'
    )

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'status', 'service', 'table', 'user_username', 'user_email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.form.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.DateInput, forms.Select)):
                field.widget.attrs.update({'class': 'form-control'})


# # bookings/forms.py
# from django import forms
# from .models import Booking, UserProfile, Table, Service
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
# from django.utils import timezone
# from datetime import timedelta
# import django_filters

# class DateTimeInput(forms.DateTimeInput):
#     input_type = 'datetime-local'

# class BookingForm(forms.ModelForm):
#     # This form is for booking a specific service, so service is often pre-filled or hidden
#     start_time = forms.DateTimeField(
#         widget=DateTimeInput,
#         help_text="Please select a date and time for your booking."
#     )

#     class Meta:
#         model = Booking
#         fields = ['service', 'start_time']

#     def __init__(self, *args, **kwargs):
#         service = kwargs.pop('service', None) # Pass service instance from view
#         super().__init__(*args, **kwargs)
#         if service:
#             self.fields['service'].initial = service.id
#             self.fields['service'].widget = forms.HiddenInput() # Hide if pre-filled

#         # Add min attribute for start_time to prevent past bookings
#         self.fields['start_time'].widget.attrs['min'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

#     def clean_start_time(self):
#         start_time = self.cleaned_data['start_time']
#         if start_time < timezone.now():
#             raise forms.ValidationError("Booking cannot be in the past.")
#         # You might add more complex validation here (e.g., only during business hours)
#         return start_time

# class ServiceSearchForm(forms.Form):
#     query = forms.CharField(
#         max_length=100,
#         required=False,
#         label='Search Services',
#         widget=forms.TextInput(attrs={'placeholder': 'e.g., Massage, Consultation'})
#     )

# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['phone_number', 'address']

# class UserRegisterForm(UserCreationForm):
#     phone_number = forms.CharField(max_length=20, required=False, help_text="Optional phone number")
#     address = forms.CharField(widget=forms.Textarea, required=False, help_text="Optional address")

#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = UserCreationForm.Meta.fields + ('email',) # Add email if you want it during registration

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data.get('email') # Save email
#         if commit:
#             user.save()
#             UserProfile.objects.create(
#                 user=user,
#                 phone_number=self.cleaned_data.get('phone_number'),
#                 address=self.cleaned_data.get('address')
#             )
#         return user
    
# class TableForm(forms.ModelForm):
#     class Meta:
#         model = Table
#         fields = ['name', 'capacity', 'is_available', 'location']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
#             'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'location': forms.TextInput(attrs={'class': 'form-control'}),
#         }

# class StaffBookingFilterForm(django_filters.FilterSet):
#     # Filter by date range (start_time of the booking)
#     start_date = django_filters.DateFilter(
#         field_name='start_time', lookup_expr='gte',
#         widget=forms.DateInput(attrs={'type': 'date'}),
#         label='Bookings From'
#     )
#     end_date = django_filters.DateFilter(
#         field_name='start_time', lookup_expr='lte',
#         widget=forms.DateInput(attrs={'type': 'date'}),
#         label='Bookings To'
#     )

#     # Filter by booking status
#     status = django_filters.ChoiceFilter(
#         choices=Booking.STATUS_CHOICES,
#         empty_label="Any Status",
#         label='Status'
#     )

#     # Filter by service
#     service = django_filters.ModelChoiceFilter(
#         queryset=Service.objects.all().order_by('name'),
#         empty_label="Any Service",
#         label='Service'
#     )

#     # Filter by table
#     table = django_filters.ModelChoiceFilter(
#         queryset=Table.objects.all().order_by('name'),
#         empty_label="Any Table",
#         label='Table'
#     )

#     # Filter by user (username or email)
#     user_username = django_filters.CharFilter(
#         field_name='user__username', lookup_expr='icontains',
#         label='User Username Contains'
#     )
#     user_email = django_filters.CharFilter(
#         field_name='user__email', lookup_expr='icontains',
#         label='User Email Contains'
#     )

#     class Meta:
#         model = Booking
#         fields = ['start_date', 'end_date', 'status', 'service', 'table', 'user_username', 'user_email']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Optional: Add generic CSS classes for styling if you use a framework
#         for name, field in self.form.fields.items():
#             if isinstance(field.widget, (forms.TextInput, forms.DateInput, forms.Select)):
#                 field.widget.attrs.update({'class': 'form-control'})

# # bookings/forms.py
# from django import forms
# from .models import Booking, UserProfile, Table, Service
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
# from django.utils import timezone
# from datetime import timedelta
# import django_filters

# class DateTimeInput(forms.DateTimeInput):
#     input_type = 'datetime-local'

# class BookingForm(forms.ModelForm):
#     start_time = forms.DateTimeField(
#         widget=DateTimeInput,
#         help_text="Please select a date and time for your booking."
#     )

#     class Meta:
#         model = Booking
#         fields = ['service', 'start_time']

#     def __init__(self, *args, **kwargs):
#         service = kwargs.pop('service', None)
#         super().__init__(*args, **kwargs)

#         if service:
#             self.fields['service'].initial = service.id
#             self.fields['service'].widget = forms.HiddenInput()

#         self.fields['start_time'].widget.attrs['min'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

#     def clean_start_time(self):
#         start_time = self.cleaned_data.get('start_time')
#         if start_time and start_time < timezone.now():
#             raise forms.ValidationError("Booking cannot be in the past.")
#         return start_time

#     def clean(self):
#         cleaned_data = super().clean()
#         service = cleaned_data.get('service')
#         start_time = cleaned_data.get('start_time')

#         if not service or not start_time:
#             return cleaned_data  # field-level errors already raised

#         overlapping = Booking.objects.filter(
#             service=service,
#             start_time=start_time,
#             status__in=['pending', 'confirmed']  # adjust as needed
#         )

#         if overlapping.exists():
#             raise forms.ValidationError("This time slot is fully booked. Please choose another time.")

#         return cleaned_data


# class ServiceSearchForm(forms.Form):
#     query = forms.CharField(
#         max_length=100,
#         required=False,
#         label='Search Services',
#         widget=forms.TextInput(attrs={'placeholder': 'e.g., Massage, Consultation'})
#     )


# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['phone_number', 'address']


# class UserRegisterForm(UserCreationForm):
#     phone_number = forms.CharField(max_length=20, required=False, help_text="Optional phone number")
#     address = forms.CharField(widget=forms.Textarea, required=False, help_text="Optional address")
#     email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = UserCreationForm.Meta.fields + ('email',)
    
#     def clean_email(self):
#         email = self.cleaned_data['email']
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("This email address is already registered.")
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data.get('email')
#         user.first_name = self.cleaned_data.get('first_name', '')
#         user.last_name = self.cleaned_data.get('last_name', '')
#         if commit:
#             user.save()
#             # Create a UserProfile for the new user
#             UserProfile.objects.create(user=user)
#         return user


# class TableForm(forms.ModelForm):
#     class Meta:
#         model = Table
#         fields = ['name', 'capacity', 'is_available', 'location']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
#             'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'location': forms.TextInput(attrs={'class': 'form-control'}),
#         }


# class StaffBookingFilterForm(django_filters.FilterSet):
#     start_date = django_filters.DateFilter(
#         field_name='start_time', lookup_expr='gte',
#         widget=forms.DateInput(attrs={'type': 'date'}),
#         label='Bookings From'
#     )
#     end_date = django_filters.DateFilter(
#         field_name='start_time', lookup_expr='lte',
#         widget=forms.DateInput(attrs={'type': 'date'}),
#         label='Bookings To'
#     )
#     status = django_filters.ChoiceFilter(
#         choices=Booking.STATUS_CHOICES,
#         empty_label="Any Status",
#         label='Status'
#     )
#     service = django_filters.ModelChoiceFilter(
#         queryset=Service.objects.all().order_by('name'),
#         empty_label="Any Service",
#         label='Service'
#     )
#     table = django_filters.ModelChoiceFilter(
#         queryset=Table.objects.all().order_by('name'),
#         empty_label="Any Table",
#         label='Table'
#     )
#     user_username = django_filters.CharFilter(
#         field_name='user__username', lookup_expr='icontains',
#         label='User Username Contains'
#     )
#     user_email = django_filters.CharFilter(
#         field_name='user__email', lookup_expr='icontains',
#         label='User Email Contains'
#     )

#     class Meta:
#         model = Booking
#         fields = ['start_date', 'end_date', 'status', 'service', 'table', 'user_username', 'user_email']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for name, field in self.form.fields.items():
#             if isinstance(field.widget, (forms.TextInput, forms.DateInput, forms.Select)):
#                 field.widget.attrs.update({'class': 'form-control'})
