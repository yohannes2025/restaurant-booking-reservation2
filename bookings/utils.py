# # # bookings/utils.py
# # import os
# # from datetime import datetime
# # from django.template.loader import render_to_string
# # from django.core.mail import EmailMessage
# # from django.conf import settings
# # from django.urls import reverse
# # from django.contrib.staticfiles import finders # For finding static files
# # from weasyprint import HTML, CSS
# # import django_rq # Import django-rq

# # def generate_booking_confirmation_pdf(booking):
# #     """
# #     Generates a PDF confirmation for a given booking.
# #     Returns the PDF content as bytes.
# #     """
# #     # Define PDF filename
# #     filename = f"booking_confirmation_{booking.id}.pdf"
    
# #     # Context for the PDF template
# #     context = {
# #         'booking': booking,
# #         'user': booking.user,
# #         'service': booking.service,
# #         'current_date': timezone.localdate(),
# #     }

# #     # Render HTML content for PDF
# #     html_string = render_to_string('bookings/pdf/booking_confirmation_pdf.html', context)
# #     html = HTML(string=html_string)

# #     # You can add CSS for the PDF here
# #     # Example to load static CSS for PDF:
# #     # css_file_path = finders.find('css/pdf_style.css') # Assuming you have static/css/pdf_style.css
# #     # if css_file_path:
# #     #     main_css = CSS(filename=css_file_path)
# #     # else:
# #     #     main_css = None # No external CSS

# #     # Basic inline CSS for the PDF if no external file is used
# #     inline_css = CSS(string='''
# #         @page { size: A4; margin: 2cm; }
# #         body { font-family: sans-serif; line-height: 1.6; color: #333; }
# #         h1, h2 { color: #2c3e50; }
# #         .header { text-align: center; margin-bottom: 30px; }
# #         .details p { margin: 5px 0; }
# #         .footer { text-align: center; margin-top: 50px; font-size: 0.8em; color: #777; }
# #         table { width: 100%; border-collapse: collapse; margin-top: 20px; }
# #         th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
# #         th { background-color: #f2f2f2; }
# #     ''')
    
# #     # Generate PDF
# #     pdf_bytes = html.write_pdf(stylesheets=[inline_css]) # Add main_css if loaded

# #     return pdf_bytes, filename

# # @django_rq.job('default') # Decorator to make this a background job
# # def send_booking_confirmation_email(booking_id):
# #     """
# #     Sends a booking confirmation email with a PDF attachment.
# #     This function will be run in a background RQ worker.
# #     """
# #     from bookings.models import Booking # Import inside function to avoid circular imports

# #     try:
# #         booking = Booking.objects.get(id=booking_id)
# #     except Booking.DoesNotExist:
# #         print(f"Booking with ID {booking_id} not found. Email not sent.")
# #         return

# #     # Generate PDF
# #     pdf_content, filename = generate_booking_confirmation_pdf(booking)

# #     # Context for the email HTML template
# #     context = {
# #         'booking': booking,
# #         'user': booking.user,
# #         'service': booking.service,
# #         'site_name': 'Your Booking System', # Use settings.SITE_NAME if you define it
# #         'booking_url': settings.BASE_URL + reverse('bookings:user_bookings'), # Assuming BASE_URL is set
# #     }

# #     # Render HTML content for the email body
# #     email_html_content = render_to_string('bookings/email/booking_confirmation_email.html', context)
# #     email_plain_content = render_to_string('bookings/email/booking_confirmation_email.txt', context) # Plain text fallback

# #     email_subject = f"Booking Confirmation for {booking.service.name}"
# #     recipient_list = [booking.user.email]

# #     # Create EmailMessage object
# #     email = EmailMessage(
# #         subject=email_subject,
# #         body=email_plain_content,
# #         from_email=settings.DEFAULT_FROM_EMAIL,
# #         to=recipient_list,
# #     )
# #     email.content_subtype = "plain" # Default to plain text
# #     email.attach_alternative(email_html_content, "text/html") # Attach HTML version

# #     # Attach PDF
# #     email.attach(filename, pdf_content, 'application/pdf')

# #     try:
# #         email.send(fail_silently=False)
# #         print(f"Confirmation email sent for Booking ID: {booking.id} to {booking.user.email}")
# #     except Exception as e:
# #         print(f"Error sending email for Booking ID {booking.id}: {e}")


# # bookings/utils.py

# import os
# from datetime import datetime
# from django.template.loader import render_to_string
# from django.core.mail import EmailMessage
# from django.conf import settings
# from django.urls import reverse
# from django.contrib.staticfiles import finders  # For finding static files
# from django.utils import timezone  # ✅ Added to support timezone.localdate()
# from weasyprint import HTML, CSS
# import django_rq  # For background job queue


# def generate_booking_confirmation_pdf(booking):
#     """
#     Generates a PDF confirmation for a given booking.
#     Returns the PDF content as bytes.
#     """
#     # Define PDF filename
#     filename = f"booking_confirmation_{booking.id}.pdf"

#     # Context for the PDF template
#     context = {
#         'booking': booking,
#         'user': booking.user,
#         'service': booking.service,
#         'current_date': timezone.localdate(),
#     }

#     # Render HTML content for the PDF
#     html_string = render_to_string('bookings/pdf/booking_confirmation_pdf.html', context)
#     html = HTML(string=html_string)

#     # Optional: Load external static CSS file for styling the PDF
#     # css_file_path = finders.find('css/pdf_style.css')
#     # if css_file_path:
#     #     main_css = CSS(filename=css_file_path)
#     # else:
#     #     main_css = None

#     # Basic inline CSS for PDF layout and formatting
#     inline_css = CSS(string='''
#         @page { size: A4; margin: 2cm; }
#         body { font-family: sans-serif; line-height: 1.6; color: #333; }
#         h1, h2 { color: #2c3e50; }
#         .header { text-align: center; margin-bottom: 30px; }
#         .details p { margin: 5px 0; }
#         .footer { text-align: center; margin-top: 50px; font-size: 0.8em; color: #777; }
#         table { width: 100%; border-collapse: collapse; margin-top: 20px; }
#         th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
#         th { background-color: #f2f2f2; }
#     ''')

#     # Generate PDF with optional CSS
#     pdf_bytes = html.write_pdf(stylesheets=[inline_css])  # Add main_css in list if using external CSS

#     return pdf_bytes, filename


# @django_rq.job('default')  # Runs this function in a background RQ worker
# def send_booking_confirmation_email(booking_id):
#     """
#     Sends a booking confirmation email with a PDF attachment.
#     This function will be run in a background RQ worker.
#     """
#     from bookings.models import Booking  # Delayed import to avoid circular dependency

#     try:
#         booking = Booking.objects.get(id=booking_id)
#     except Booking.DoesNotExist:
#         print(f"Booking with ID {booking_id} not found. Email not sent.")
#         return

#     # Generate PDF attachment
#     pdf_content, filename = generate_booking_confirmation_pdf(booking)

#     # Context for email templates
#     context = {
#         'booking': booking,
#         'user': booking.user,
#         'service': booking.service,
#         'site_name': 'Your Booking System',  # You can set SITE_NAME in settings.py
#         'booking_url': settings.BASE_URL + reverse('bookings:user_bookings'),  # Assumes BASE_URL is in settings.py
#     }

#     # Render email contents
#     email_html_content = render_to_string('bookings/email/booking_confirmation_email.html', context)
#     email_plain_content = render_to_string('bookings/email/booking_confirmation_email.txt', context)

#     email_subject = f"Booking Confirmation for {booking.service.name}"
#     recipient_list = [booking.user.email]

#     # Create email message
#     email = EmailMessage(
#         subject=email_subject,
#         body=email_plain_content,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=recipient_list,
#     )
#     email.content_subtype = "plain"  # Fallback content type
#     email.attach_alternative(email_html_content, "text/html")  # HTML version

#     # Attach the generated PDF
#     email.attach(filename, pdf_content, 'application/pdf')

#     # Send email
#     try:
#         email.send(fail_silently=False)
#         print(f"Confirmation email sent for Booking ID: {booking.id} to {booking.user.email}")
#     except Exception as e:
#         print(f"Error sending email for Booking ID {booking.id}: {e}")


# bookings/utils.py

import os
from datetime import datetime
from django.template.loader import render_to_string
from django.core.mail import EmailMessage # EmailMessage can handle HTML alternatives and attachments
from django.conf import settings
from django.urls import reverse
from django.contrib.staticfiles import finders  # For finding static files
from django.utils import timezone  # ✅ Added to support timezone.localdate()
from weasyprint import HTML, CSS
import django_rq  # For background job queue


def generate_booking_confirmation_pdf(booking):
    """
    Generates a PDF confirmation for a given booking.
    Returns the PDF content as bytes.
    """
    # Define PDF filename
    filename = f"booking_confirmation_{booking.id}.pdf"

    # Context for the PDF template
    context = {
        'booking': booking,
        'user': booking.user,
        'service': booking.service,
        'current_date': timezone.localdate(),
    }

    # Render HTML content for the PDF
    html_string = render_to_string('bookings/pdf/booking_confirmation_pdf.html', context)
    html = HTML(string=html_string)

    # Optional: Load external static CSS file for styling the PDF
    # css_file_path = finders.find('css/pdf_style.css')
    # if css_file_path:
    #    main_css = CSS(filename=css_file_path)
    # else:
    #    main_css = None

    # Basic inline CSS for PDF layout and formatting
    inline_css = CSS(string='''
        @page { size: A4; margin: 2cm; }
        body { font-family: sans-serif; line-height: 1.6; color: #333; }
        h1, h2 { color: #2c3e50; }
        .header { text-align: center; margin-bottom: 30px; }
        .details p { margin: 5px 0; }
        .footer { text-align: center; margin-top: 50px; font-size: 0.8em; color: #777; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    ''')

    # Generate PDF with optional CSS
    pdf_bytes = html.write_pdf(stylesheets=[inline_css])  # Add main_css in list if using external CSS

    return pdf_bytes, filename


@django_rq.job('default')  # Runs this function in a background RQ worker
def send_booking_confirmation_email(booking_id):
    """
    Sends a booking confirmation email with a PDF attachment.
    This function will be run in a background RQ worker.
    """
    from bookings.models import Booking  # Delayed import to avoid circular dependency

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        print(f"Booking with ID {booking_id} not found. Email not sent.")
        return

    # Generate PDF attachment
    pdf_content, filename = generate_booking_confirmation_pdf(booking)

    # Context for email templates
    context = {
        'booking': booking,
        'user': booking.user, # This 'user' object now has the email from registration
        'service': booking.service,
        'site_name': 'Your Booking System',  # You can set SITE_NAME in settings.py
        'booking_url': settings.BASE_URL + reverse('bookings:user_bookings'),  # Assumes BASE_URL is in settings.py
    }

    # Render email contents
    email_html_content = render_to_string('bookings/email/booking_confirmation_email.html', context)
    email_plain_content = render_to_string('bookings/email/booking_confirmation_email.txt', context)

    email_subject = f"Booking Confirmation for {booking.service.name}"
    # The recipient list correctly uses the user's email from the booking
    recipient_list = [booking.user.email]

    # Create email message. EmailMessage handles multiple content types and attachments.
    email = EmailMessage(
        subject=email_subject,
        body=email_plain_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )
    email.content_subtype = "plain"  # Fallback content type
    email.attach_alternative(email_html_content, "text/html")  # HTML version

    # Attach the generated PDF
    email.attach(filename, pdf_content, 'application/pdf')

    # Send email
    try:
        email.send(fail_silently=False)
        print(f"Confirmation email sent for Booking ID: {booking.id} to {booking.user.email}")
    except Exception as e:
        print(f"Error sending email for Booking ID {booking.id}: {e}")
