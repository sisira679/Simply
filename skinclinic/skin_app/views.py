from django.shortcuts import render, redirect,get_object_or_404, redirect
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from .models import CustomUser  # Ensure the correct import path for CustomUser model
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required,user_passes_test
from .forms import DoctorForm,PharmacistForm
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile
from datetime import datetime
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password 
from .models import DoctorProfile
from .models import Specializations
from .forms import SpecializationsForm
from .forms import DateSelectionForm
from django.db.models import Q
from .models import DoctorSchedule
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import EditDoctorForm, EditSpecializationsForm
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from .forms import AppointmentForm
from .models import Appointment
# from .forms import BookingForm
# from .models import Booking
from .models import DoctorLeave
from .forms import LeaveForm
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import uuid
# from .forms import PrescriptionForm
# from .models import  Prescription
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .forms import  PaymentForm
from .models import Payment
from django.contrib.auth.forms import AuthenticationForm

def doctor_list(request):
    query = request.GET.get('q')  # Get the search query from the URL parameter 'q'

    if query:
        # If a search query is provided, filter doctors whose first_name starts with the query
        doctors = CustomUser.objects.filter(role='Doctor', first_name__istartswith=query).prefetch_related('specializations')
    else:
        # If no search query is provided, fetch all doctors
        doctors = CustomUser.objects.filter(role='Doctor').prefetch_related('specializations')

    # Check if the request is an AJAX request
    if request.is_ajax():
        # If it's an AJAX request, return JSON response with the search results
        data = []
        for doctor in doctors:
            data.append({
                'username': doctor.username,
                'email': doctor.email,
                'first_name': doctor.first_name,
                'last_name': doctor.last_name,
                'role': doctor.role,
                'specializations': [specialization.get_specializations_display() for specialization in doctor.specializations.all()]
            })
        return JsonResponse({'users': data, 'query': query})

    # If it's not an AJAX request, render the HTML template with the search results
    return render(request, 'doctor-list.html', {'users': doctors, 'query': query})

def index(request): 
    return render(request, 'index.html')

@login_required  # Ensure only authenticated users can access this view
def userdashboard(request): 
    appointments = Appointment.objects.filter(user=request.user)
    doctors = CustomUser.objects.filter(role='Doctor')[:5]  # Query only the first five doctors
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    doctor_profile, created = DoctorProfile.objects.get_or_create(user=request.user)
    products = Product.objects.filter(status='ACTIVE')
    
    # Handling appointments
    appointment = appointments.first() if appointments.exists() else None  
    
    return render(request, 'userdashboard.html', {
        'user_profile': user_profile,
        'doctors': doctors,  # Renamed from 'users' to 'doctors'
        'doctor_profile': doctor_profile,
        'appointment': appointment,
        'products': products,  # Passing products to the template
    })
def register(request):
    if request.method == 'POST':
       
        username = request.POST['username']
        email = request.POST['email']
        role = request.POST.get('role', None)
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender=request.POST.get('gender')

         # Check if the email already exists in the database
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error_message': 'Email address is already in use.'})


        if password != confirm_password:
            # Handle password mismatch error
            return render(request, 'register.html', {'error_message': 'Passwords do not match'})
        
        # Create a new user object
        user = CustomUser.objects.create_user(username=username, email=email, password=password,role=role, first_name=first_name,
                    last_name=last_name,gender=gender)
        messages.success(request, 'Account created successfully. You can now log in.')

        # You don't need to call login here because the user is already authenticated
        # You can directly redirect to the dashboard after successful registration
        return redirect('login')

    return render(request, 'register.html')


def logout(request):
    auth_logout(request) # Use the logout function to log the user out
    return redirect('login')  # Redirect to the confirmation page

    
@login_required(login_url='login')
def indexadmin(request):
    num_patients = CustomUser.objects.filter(role='User').count()
    num_doctors = CustomUser.objects.filter(role='Doctor').count()
    return render(request, 'indexadmin.html', {'num_patients': num_patients,'num_doctors': num_doctors})





def user_login(request):
    appointment = Appointment.objects.first()  # Example: Get the first appointment object

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)

                if user.role == "pharmacist":
                    request.session['username'] = username
                    return redirect("pharmacistdashboard")
                elif user.role == "Doctor":
                    doctor_profile, created = DoctorProfile.objects.get_or_create(user=user)
                    if created or not doctor_profile.is_profile_complete():
                        return redirect("update_profile")
                    else:
                        return redirect("doctordashboard")
                elif user.role == "User":
                    request.session['username'] = username
                    return redirect("userdashboard")
                elif user.role == "DeliveryBoy":
                    request.session['username'] = username
                    return redirect("availableorder")
                elif user.username == "admin":
                    request.session['username'] = username
                    return redirect("indexadmin")
                
            else:
                messages.error(request, "Incorrect username or password. Please try again.")
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
               # Pass the appointment object to the context
    context = {
        'appointment': appointment
    }

    return render(request, 'login.html')

from django.core.mail import send_mail
from django.conf import settings

def add_doctor(request):
    if request.method == 'POST':
        doctor_form = DoctorForm(request.POST)
        specializations_form = SpecializationsForm(request.POST)
        if doctor_form.is_valid() and specializations_form.is_valid():
            user = doctor_form.save(commit=False)
            password = doctor_form.cleaned_data['password']
            user.set_password(password)
            user.save()

            # Get the selected specialization from the SpecializationsForm
            specialization = specializations_form.cleaned_data['specializations']

            # Create Specializations instance and associate it with the user
            specializations, created = Specializations.objects.get_or_create(user=user)
            specializations.specializations = specialization
            specializations.save()

            # Sending email to the user
            
            # Sending email to the user
            subject = 'Registered Successfully'
            messages = f'Dear {user.username},\n\nYour account has been successfully created by an admin'
            message = f'Here are your login details:\n\nUsername: {user.username}\nPassword: {password}\n\nPlease login using these credentials. Thank you.'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = user.email
            send_mail(subject, message,messages, from_email, [to_email])
            return redirect('doctorprofile_list.html')
    else:
        doctor_form = DoctorForm()
        specializations_form = SpecializationsForm()

    return render(request, 'add-doctor.html', {'doctor_form': doctor_form, 'specializations_form': specializations_form})


def add_pharmacist(request):
    if request.method == 'POST':
        pharmacist_form = PharmacistForm(request.POST)
        if pharmacist_form.is_valid():
            user = pharmacist_form.save(commit=False)
            password = pharmacist_form.cleaned_data['password']
            user.set_password(password)
            user.save()

            subject = 'Registration Confirmation'
            message = f'You are added to our hospital \n\nUsername: {user.username}\nPassword: {password}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return redirect('pharmacist-list.html')
    else:
        pharmacist_form = PharmacistForm()

    return render(request, 'add-pharmacist.html', {'pharmacist_form': pharmacist_form})



@login_required(login_url='login')
def pharmacistdashboard(request):
    products = Product.objects.all()
    num_products = products.count()  # Count the number of products
    return render(request, 'pharmacistdashboard.html', {'products': products, 'num_products': num_products})



def user_list(request):
     user = CustomUser.objects.filter(role='User')

     return render(request, 'user_list.html', {'users': user})


def pharmacist_list(request):
    pharmacists = CustomUser.objects.filter(role='pharmacists')
    return render(request, 'pharmacist-list.html', {'pharmacists': pharmacists})






      


def doctor_list(request):
    query = request.GET.get('q')  # Get the search query from the URL parameter 'q'

    if query:
        # If a search query is provided, filter doctors whose first_name starts with the query
        doctors = CustomUser.objects.filter(role='Doctor', first_name__istartswith=query).prefetch_related('specializations')
    else:
        # If no search query is provided, fetch all doctors
        doctors = CustomUser.objects.filter(role='Doctor').prefetch_related('specializations')

    return render(request, 'doctor-list.html', {'users': doctors, 'query': query})

def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(CustomUser, pk=doctor_id)
    # Delete the doctor or perform the desired action
    if request.method == 'POST':
         doctor.delete()
         messages.success(request, f'Doctor {doctor.username} has been deleted.')
         return redirect('doctor-list') 
    return render(request, 'delete-doctor.html', {'doctor': doctor})

def doctor_dashboard(request):
    doctor_profile, created = DoctorProfile.objects.get_or_create(user=request.user)
    return render(request, 'doctordashboard.html',{'doctor_profile': doctor_profile})

def user_list(request):
     user = CustomUser.objects.filter(role='User')

     return render(request, 'user_list.html', {'users': user})

def profile_user(request):
     return render(request, 'profileuser.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserProfile
import requests

@login_required(login_url='login')
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    indian_states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
        "Goa", "Gujarat", "Haryana","Himachal Pradesh", "Jharkhand", "Karnataka", 
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", 
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", 
        "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
        # Add more states as needed
    ]

    if request.method == 'POST':
        user_profile.phonenumber = request.POST.get('phonenumber')
        user_profile.address = request.POST.get('address') 
        user_profile.dob = request.POST.get('dob')
        user_profile.age = request.POST.get('age')
        user_profile.state = request.POST.get('state')
        user_profile.city = request.POST.get('city')
        user_profile.district = request.POST.get('district')
        user_profile.pincode = request.POST.get('pincode')
        user_profile.bloodgroup = request.POST.get('bloodgroup')

        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']

        user_profile.save()

        return redirect('profile')

    return render(request, 'profile.html', {'indian_states': indian_states, 'user_profile': user_profile, 'created': created})
from django.contrib.auth.hashers import check_password  # Import check_password

@login_required(login_url='login')
def changepassword(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']

        # Check if old password matches the existing password
        if check_password(old_password, request.user.password) and new_password1 == new_password2:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Pass the user object as the second argument
            messages.success(request, 'Password changed successfully!')
            
            return redirect('login')  # Redirect to profile page or any other page you prefer
        else:
            messages.error(request, 'Password change failed. Please check your old password or new password confirmation.')

    return render(request, 'changepassword.html')



@login_required(login_url='login')
def doctorprofile(request):
    doctor_profile, created = DoctorProfile.objects.get_or_create(user=request.user)
    indian_states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", 
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", 
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", 
        "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
        # Add more states as needed
    ]


    if request.method == 'POST':
        # Process form data manually
        doctor_profile.phonenumber = request.POST.get('phonenumber')
        doctor_profile.address = request.POST.get('address')
        doctor_profile.dob = request.POST.get('dob')
        doctor_profile.age = request.POST.get('age')
        doctor_profile.state = request.POST.get('state')
        doctor_profile.bloodgroup = request.POST.get('bloodgroup')
        doctor_profile.city = request.POST.get('city')
        doctor_profile.consultation_fee = request.POST.get('consultation_fee')  # Add this line


        # Handle image upload for ID proof
        # Handle image upload manually
        if 'profile_picture' in request.FILES:
            doctor_profile.profile_picture = request.FILES['profile_picture']
        else:
                # Handle the case when the uploaded file is not a PNG, JPG, or JPEG
                # You may want to show an error message or take other actions
                pass
        if 'id_proof_image' in request.FILES:
            doctor_profile.id_proof_image = request.FILES['id_proof_image']
        else:
            # Handle the case when the uploaded file is not a PNG, JPG, or JPEG
            # You may want to show an error message or take other actions
              pass
          # Handle PDF uploads
        for i in range(1, 4):
            pdf_field_name = f'pdf_certificate_{i}'
            if pdf_field_name in request.FILES:
                pdf_file = request.FILES[pdf_field_name]
                if pdf_file.content_type == 'application/pdf':
                    setattr(doctor_profile, pdf_field_name, pdf_file)
                else:
                    # Handle the case when the uploaded file is not a PDF
                    # You may want to show an error message or take other actions
                    pass
                 

        doctor_profile.save()

        # Redirect to a success page or update the current page as needed
        return redirect('doctorprofile')

    return render(request, 'doctorprofile.html', {'indian_states': indian_states, 'doctor_profile': doctor_profile, 'created': created})




def doctordetails(request):
    return render(request,'doctordetails.html')


def add_brand(request):
    return render(request,'add_brand.html')
def add_category(request):
    return render(request,'add_category.html')


def specializations(request):
    specializations, created = Specializations.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Process form data manually
        specializations.specialization_type = request.POST.get('specializations')
        specializations.save()
        return redirect('specializations')  # Correct the redirect statement

    return render(request, 'specializations.html', {'specializations': specializations, 'created': created})

def alldoctor(request):
      user_profile, created = UserProfile.objects.get_or_create(user=request.user)
      doctors = CustomUser.objects.filter(role='Doctor')
      return render(request, 'alldoctorlist.html', {'doctors': doctors,'user_profile': user_profile})


def booking_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    doctor_profile, created = DoctorProfile.objects.get_or_create(user=request.user)
    selected_specialization = request.GET.get('specializations')
   
    doctors = CustomUser.objects.filter(role='Doctor', specializations=selected_specialization)
    return render(request, 'booking.html', {'users': doctors, 'doctor_profile': doctor_profile})
 


# def appointment(request):
#     user_profile, created = UserProfile.objects.get_or_create(user=request.user)
#     selected_specialization = request.GET.get('specializations', None)

#     if request.method == 'GET' and selected_specialization:
#         doctors = CustomUser.objects.filter(role='Doctor', specializations__specializations=selected_specialization)
#     else:
#         doctors = CustomUser.objects.filter(role='Doctor')

#     specializations = Specializations.objects.all()

#     return render(request, 'appointment.html', {'doctors': doctors, 'user_profile': user_profile, 'specializations': specializations, 'selected_specialization': selected_specialization})

from datetime import datetime
def appointment(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    selected_specialization = request.GET.get('specializations', None)

    if request.method == 'GET' and selected_specialization:
        doctors = CustomUser.objects.filter(role='Doctor', specializations__specializations=selected_specialization)
    else:
        doctors = CustomUser.objects.filter(role='Doctor')

    specializations = Specializations.objects.all()

    # Get leave information for all doctors
    leave_data = get_leave_data()

    # Check if each doctor is on leave for the current day
    today = datetime.now().strftime('%Y-%m-%d')
    for doctor in doctors:
        doctor.on_leave = today in leave_data.get(doctor.id, [])

    return render(request, 'appointment.html', {'doctors': doctors, 'user_profile': user_profile, 'specializations': specializations, 'selected_specialization': selected_specialization})
def get_leave_data():
    # Retrieve leave data from DoctorLeave model
    leave_data = {}
    leave_objects = DoctorLeave.objects.all()

    for leave_object in leave_objects:
        doctor_id = leave_object.doctor.id
        leave_date = leave_object.date.strftime('%Y-%m-%d')

        if doctor_id not in leave_data:
            leave_data[doctor_id] = []

        leave_data[doctor_id].append(leave_date)

    return leave_data



     


def doctor_list_api(request):
    query = request.GET.get('q', '')
    doctors = CustomUser.objects.filter(role='Doctor', first_name__istartswith=query).prefetch_related('specializations')
    doctors_data = []
    for doctor in doctors:
        doctor_data = {
            'id': doctor.id,
            'username': doctor.username,
            'email': doctor.email,
            'first_name': doctor.first_name,
            'last_name': doctor.last_name,
            'role': doctor.role,
            'specializations': [specialization.get_specializations_display() for specialization in doctor.specializations.all()],
            'delete_url': reverse('delete-doctor', args=[doctor.id])
        }
        doctors_data.append(doctor_data)
    return JsonResponse(doctors_data, safe=False)

# @login_required
# def scheduling(request):
#     if request.method == 'POST':
#         date = request.POST['date']
#         time_slot = request.POST['time_slot']

#         # Check if the user is a doctor
#         if request.user.role == 'Doctor':
#             # Check if the schedule already exists for the given date and time slot
#             existing_schedule = DoctorSchedule.objects.filter(user=request.user, date=date, time_slot=time_slot)
#             if existing_schedule.exists():
#                 messages.error(request, 'Schedule already exists for this date and time slot.')
#             else:
#                 # If not, create and save the schedule
#                 schedule = DoctorSchedule.objects.create(user=request.user, date=date, time_slot=time_slot)
#                 schedule.save()
#         else:
#             # Handle the case when the user is not a doctor
#             messages.error(request, 'You are not a registered doctor.')

#     # Fetch existing schedules for the current doctor
#     doctor_schedules = DoctorSchedule.objects.filter(user=request.user)

#     return render(request, 'scheduling.html', {'doctor_schedules': doctor_schedules})

from django.core.exceptions import ValidationError

@login_required
def scheduling(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')

        # Check if the date and time slot are present in the POST request
        if not date or not time_slot:
            messages.error(request, 'Please select a date and time slot.')
        else:
            # Check if the user is a doctor
            if request.user.role == 'Doctor':
                # Check if the schedule already exists for the given date and time slot
                existing_schedule = DoctorSchedule.objects.filter(user=request.user, date=date, time_slot=time_slot)
                if existing_schedule.exists():
                    messages.error(request, 'Schedule already exists for this date and time slot.')
                else:
                    # If not, create and save the schedule
                    schedule = DoctorSchedule.objects.create(user=request.user, date=date, time_slot=time_slot)
                    schedule.save()
            else:
                # Handle the case when the user is not a doctor
                messages.error(request, 'You are not a registered doctor.')

    # Fetch existing schedules for the current doctor
    doctor_schedules = DoctorSchedule.objects.filter(user=request.user)

    return render(request, 'scheduling.html', {'doctor_schedules': doctor_schedules})


# @login_required
# def book_appointment(request, user_id):
    

#     user = get_object_or_404(CustomUser, id=user_id)
#     form = DateSelectionForm(request.POST or None)

#     if form.is_valid():
#         selected_date = form.cleaned_data['date']
#         if user.role == 'Doctor':
#             available_slots = DoctorSchedule.objects.filter(user=user, date=selected_date)
#         else:
#             # Handle the case when the user is not a doctor
#             available_slots = []
#     else:
#         available_slots = []
#          # Retrieve the DoctorProfile associated with the user
#     doctor_profile = DoctorProfile.objects.get(user=user)
  
#     return render(request, 'booking.html', {'doctor_name': user.first_name, 'form': form, 'available_slots': available_slots, 'doctor_profile': doctor_profile,'doctor_email': user.email })




# views.py
@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(CustomUser, id=doctor_id, role='Doctor')
    doctor_profile = DoctorProfile.objects.get(user=doctor)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)

        if form.is_valid():
            # Set the doctor and user fields before saving
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.consultation_fee = doctor_profile.consultation_fee
            appointment.user = request.user
            appointment.doctor_profile = doctor_profile
            appointment.save()

            messages.success(request, 'Appointment booked successfully.')

            # Redirect to the confirmation page with the ap
            # pointment ID
            return redirect('payment', appointment_id=appointment.id)
        else:
            messages.error(request, 'Form is not valid. Please check your inputs.')
    else:
        form = AppointmentForm()

    # Fetch available schedules for the current doctor
    doctor_schedules = DoctorSchedule.objects.filter(user=doctor)

    return render(request, 'booking.html', {'doctor': doctor, 'user_profile': user_profile,'doctor_schedules': doctor_schedules, 'doctor_profile': doctor_profile,'form': form})


# def appointment_confirmation(request, appointment_id):
#     appointment = get_object_or_404(Appointment, id=appointment_id)
#     doctor = get_object_or_404(CustomUser, id=doctor_id, role='Doctor')
#     doctor_profile = DoctorProfile.objects.get(user=doctor)
#     user_profile, created = UserProfile.objects.get_or_create(user=request.user)

#     return render(request, 'appointment_confirmation.html', {'appointment': appointment})




# def appointment_confirmation(request, appointment_id):
#     appointment = get_object_or_404(Appointment, id=appointment_id)
#     user_profile, created = UserProfile.objects.get_or_create(user=request.user)

#     return render(
#         request,
#         'appointment_confirmation.html',
#         {
#             'appointment': appointment,
#             'doctor': appointment.doctor,
#             'user': appointment.user,
#             'user_profile': user_profile

#         }
#     )
  
@login_required
def doctordashboard(request):
    # Fetch all appointments for the current doctor
    doctor_appointments = Appointment.objects.filter(doctor=request.user).order_by('-date')

    return render(request, 'doctor_dashboard.html', {'doctor_appointments': doctor_appointments})

@login_required
def doctor_dashboard(request):
    doctor_profile, created = DoctorProfile.objects.get_or_create(user=request.user)
    return render(request, 'doctordashboard.html', {'doctor_profile': doctor_profile})


from django.shortcuts import render, redirect
# from .forms import DateSelectionForm
# from .models import DoctorSchedule

def confirm_booking(request):
    if request.method == 'POST':
        doctor_id = request.POST['doctor_id']
        selected_time_slot_id = request.POST['time_slot']

        # Process the selected time slot and doctor_id as needed

        # Redirect to the confirmation page or perform other actions
        return redirect('confirmation_page')

    # Handle GET requests if needed
    return render(request, 'book_doctor_appointment.html')

def confirm_booking(request):
    if request.method == 'POST':
        # Extract values from the form data
        selected_slot = request.POST.get('selected_slot')
        doctor_name = request.POST.get('doctor_name')

        # Process the appointment confirmation logic here

        # Pass values to the confirmation template
        context = {'selected_slot': selected_slot, 'doctor_name': doctor_name}
        return render(request, 'confirm_booking.html', context)
    else:
        return HttpResponse("Invalid Request")



@user_passes_test(lambda u: u.is_staff)
def edit_doctor(request, doctor_id):
    user = get_object_or_404(CustomUser, id=doctor_id)
    specializations, created = Specializations.objects.get_or_create(user=user)

    if request.method == 'POST':
        doctor_form = EditDoctorForm(request.POST, instance=user)
        specializations_form = EditSpecializationsForm(request.POST, instance=specializations)

        if doctor_form.is_valid() and specializations_form.is_valid():
            doctor_form.save()
            specializations_form.save()

            return redirect('doctor_list')  # Assuming the name of your URL pattern is 'doctor_list'

    else:
        doctor_form = EditDoctorForm(instance=user)
        specializations_form = EditSpecializationsForm(instance=specializations)

    return render(request, 'edit-doctor.html', {'doctor_form': doctor_form, 'specializations_form': specializations_form})


def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(DoctorSchedule, id=schedule_id)
    schedule.delete()
    return redirect('scheduling') 

def doctorprofile_list(request):
    doctors = DoctorProfile.objects.prefetch_related('user__specializations').all()
    user = CustomUser.objects.filter(role='Doctor')
    return render(request, 'doctorprofile_list.html', {'doctors': doctors,"user":user})

@login_required(login_url='login')
def update_profile(request):
    doctor_profile, created = DoctorProfile.objects.get_or_create(user=request.user)

    return render(request, 'update_profile.html', {'created': created})
# def get_time_slots(request, selected_date):
#     doctor_id = request.GET.get('doctor_id')
#     doctor = get_object_or_404(CustomUser, id=doctor_id, role='Doctor')

#     # Fetch time slots for the selected date and doctor
#     time_slots = DoctorSchedule.objects.filter(user=doctor, date=selected_date).values_list('time_slot', flat=True)

#     # Convert the QuerySet to a list and return as JSON
#     return JsonResponse(list(time_slots), safe=False)
def get_time_slots(request, selected_date):
    doctor_id = request.GET.get('doctor_id')
    doctor = get_object_or_404(CustomUser, id=doctor_id, role='Doctor')

    # Fetch available and booked time slots for the selected date and doctor
    available_time_slots = DoctorSchedule.objects.filter(user=doctor, date=selected_date).values_list('time_slot', flat=True)
    booked_time_slots = Appointment.objects.filter(doctor=doctor, date=selected_date).values_list('time_slot', flat=True)

    # Convert the QuerySets to lists and return as JSON
    return JsonResponse({'available': list(available_time_slots), 'booked': list(booked_time_slots)})



from .models import DoctorLeave
from .forms import LeaveForm

@login_required
def apply_leave(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.doctor = request.user
            leave.save()
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('doctor_leave')
    else:
        form = LeaveForm()

    return render(request, 'apply_leave.html', {'form': form})

@login_required
def doctor_leave(request):
    leave_requests = DoctorLeave.objects.filter(doctor=request.user)
    return render(request, 'doctor_leave.html', {'leave_requests': leave_requests})

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-admin users

    pending_leave_requests = DoctorLeave.objects.filter(is_approved=False)
    return render(request, 'admin_dashboard.html', {'pending_leave_requests': pending_leave_requests})

@login_required
def approve_leave(request, leave_id):
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-admin users

    leave_request = DoctorLeave.objects.get(pk=leave_id)
    leave_request.is_approved = True
    leave_request.save()

    messages.success(request, 'Leave request approved.')
    return redirect('admin_dashboard')

@login_required
def reject_leave(request, leave_id):
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-admin users

    leave_request = get_object_or_404(DoctorLeave, pk=leave_id)
    
    # Update the status to "Rejected" instead of deleting the leave request
    leave_request.is_approved = False
    leave_request.save()

    messages.success(request, 'Leave request rejected.')
    return redirect('admin_dashboard')

@login_required
def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointment_confirmation.html', {'appointment': appointment})

@login_required
def payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'payment.html', {'appointment': appointment})

@login_required
def process_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Check the selected payment option
    payment_option = request.POST.get('payment_option')

    if payment_option == 'online':
        # Implement your online payment logic here
        # For example, you can integrate with a payment gateway

        messages.success(request, 'Payment successful. Appointment confirmed.')
        return redirect('success_page')

    elif payment_option == 'hospital':
        # Generate a token and send it to the user's email
        token = generate_token()

        # Send an email to the user with the token
        send_mail(
            'Hospital Payment Token',
            f'Your payment token is: {token}',
            settings.EMAIL_HOST_USER ,
            [appointment.user.email],
            fail_silently=False,
        )

        messages.success(request, 'Hospital payment initiated. Check your email for the payment token.')
        return redirect('success_page')

    else:
        messages.error(request, 'Invalid payment option selected.')
        return redirect('appointment_confirmation', appointment_id=appointment.id)

def generate_token():
    # Implement your token generation logic here
    # This is a simple example; you may want to use a more secure method
    import random
    return str(random.randint(100000, 999999))



from django.utils import timezone

def today_appointments(request):   # type: ignore
    today = timezone.now().date()
    
    # Assuming the doctor information is stored in the request.user
    doctor = request.user  # Adjust this based on your authentication system

    # Filter appointments for the current doctor and today's date
    today_appointments = Appointment.objects.filter(doctor=doctor, date=today)

    return render(request, 'today_appointments.html', {'today_appointments': today_appointments})



@login_required
def verify_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    payment = get_object_or_404(Payment, appointment=appointment)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        if entered_otp == payment.otp:
            messages.success(request, 'Payment successful!')
            return redirect('payment_success')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'verify_payment.html', {'appointment': appointment})

# Add this function in your views.py or create a new utils.py file
from django.core.mail import send_mail

def send_otp_email(to_email, otp):
    subject = 'Payment OTP'
    message = f'SIMPLY SKIN CLINIC to verify your booking Your OTP for the conforimation is: {otp}'
    from_email = 'sisiras2024b@mca.ajce.in'  # Change this to your email

    send_mail(subject, message, from_email, [to_email])


def payment_success(request):
    return render(request, 'payment_success.html')

import razorpay # type: ignore
import random

# razorpay_client = razorpay.Client(auth=("rzp_test_sfFJaXgQPv4B3T", "vwLALrKy2MeB3dnNFTQs0Fdu"))

# @login_required
# def payment(request, appointment_id):
#     appointment = get_object_or_404(Appointment, id=appointment_id)

#     if request.method == 'POST':
#         payment_form = PaymentForm(request.POST)

#         if payment_form.is_valid():
#             payment_method = payment_form.cleaned_data['method']
            
#             try:
#                 # Try to get an existing Payment object for the appointment
#                 payment = Payment.objects.get(appointment=appointment)
#             except Payment.DoesNotExist:
#                 # If the Payment object doesn't exist, create a new one
#                 payment = Payment(appointment=appointment)

#             if payment_method == 'online':
#                 # For online payments using Razorpay
#                 # Create a Razorpay order and fetch the order ID
#                 default_consultation_fee = 1000
#                 order_amount = (
#                     int(appointment.doctor_profile.consultation_fee * 100)
#                     if hasattr(appointment, 'doctor_profile') and appointment.doctor_profile
#                     else default_consultation_fee
#                 )
#                 order_currency = 'INR'
#                 order_receipt = 'order_rcptid_' + str(random.randint(1000, 9999))

#                 order_response = razorpay_client.order.create({
#                     'amount': order_amount,
#                     'currency': order_currency,
#                     'receipt': order_receipt,
#                     'payment_capture': '1',  # Auto capture payment
#                 })

#                 payment.razorpay_order_id = order_response['id']

#             # Update other fields in the Payment model based on your form data
#             payment.method = payment_method
#             payment.otp = str(random.randint(100000, 999999))
            
#             payment.save()

#             if payment_method == 'online':
#                 # Redirect to Razorpay payment page
#                 return render(request, 'razorpay_payment.html', {'payment': payment})
#             else:
#                 # Send an email with the OTP to the user's registered email
#                 send_otp_email(appointment.user.email, payment.otp)
#                 return redirect('verify_payment', appointment_id=appointment.id)

#     else:
#         payment_form = PaymentForm()

#     return render(request, 'payment.html', {'appointment': appointment, 'payment_form': payment_form})


razorpay_client = razorpay.Client(auth=("rzp_test_sfFJaXgQPv4B3T", "vwLALrKy2MeB3dnNFTQs0Fdu"))
# views.py


# def payment(request, appointment_id):
#     appointment = get_object_or_404(Appointment, id=appointment_id)
#     doctor_profile, created = DoctorProfile.objects.get_or_create(user=request.user)

#     if request.method == 'POST':
#         payment_form = PaymentForm(request.POST)

#         if payment_form.is_valid():
#             payment_method = payment_form.cleaned_data['method']
            
#             try:
#                 payment = Payment.objects.get(appointment=appointment)
#             except Payment.DoesNotExist:
#                 payment = Payment(appointment=appointment)

#             if payment_method == 'online':
#                 # Get the consultation fee from the DoctorProfile
#                 doctor_consultation_fee = (
#                     appointment.doctor_profile.consultation_fee
#                     if hasattr(appointment, 'doctor_profile') and appointment.doctor_profile
#                     else 500
#                 )

#                 order_amount = int(doctor_consultation_fee * 100)
#                 order_currency = 'INR'
#                 order_receipt = 'order_rcptid_' + str(random.randint(1000, 9999))

#                 order_response = razorpay_client.order.create({
#                     'amount': order_amount,
#                     'currency': order_currency,
#                     'receipt': order_receipt,
#                     'payment_capture': '1',
#                 })

#                 payment.razorpay_order_id = order_response['id']

#             payment.method = payment_method
#             payment.otp = str(random.randint(100000, 999999))
#             payment.save()

#             if payment_method == 'online':
#                 return render(request, 'razorpay_payment.html', {'payment': payment, 'doctor_consultation_fee': doctor_consultation_fee})
#             else:
#                 send_otp_email(appointment.user.email, payment.otp)
#                 return redirect('verify_payment', appointment_id=appointment.id)

#     else:
#         payment_form = PaymentForm()

#     return render(request, 'payment.html', {'appointment': appointment, 'payment_form': payment_form, 'doctor_profile': doctor_profile})







# views.py
from .models import DoctorProfile

def payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Use the doctor associated with the appointment
    doctor_profile, created = DoctorProfile.objects.get_or_create(user=appointment.doctor)

    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)

        if payment_form.is_valid():
            payment_method = payment_form.cleaned_data['method']
            
            try:
                payment = Payment.objects.get(appointment=appointment)
            except Payment.DoesNotExist:
                payment = Payment(appointment=appointment)

            if payment_method == 'online':
                # Get the consultation fee from the DoctorProfile
                doctor_consultation_fee = getattr(doctor_profile, 'consultation_fee', 500)

                order_amount = int(doctor_consultation_fee * 100)
                order_currency = 'INR'
                order_receipt = 'order_rcptid_' + str(random.randint(1000, 9999))

                order_response = razorpay_client.order.create({
                    'amount': order_amount,
                    'currency': order_currency,
                    'receipt': order_receipt,
                    'payment_capture': '1',
                })

                payment.razorpay_order_id = order_response['id']

            payment.method = payment_method
            payment.otp = str(random.randint(100000, 999999))
            payment.save()

            if payment_method == 'online':
                return render(request, 'razorpay_payment.html', {'payment': payment, 'doctor_consultation_fee': doctor_consultation_fee})
            else:
                send_otp_email(appointment.user.email, payment.otp)
                return redirect('verify_payment', appointment_id=appointment.id)

    else:
        payment_form = PaymentForm()

    return render(request, 'payment.html', {'appointment': appointment, 'payment_form': payment_form, 'doctor_profile': doctor_profile})






from django.shortcuts import render, redirect
from .forms import PrescriptionForm
from .models import Appointment, Prescription

def add_prescription(request, appointment_id):
    appointment = Appointment.objects.get(pk=appointment_id)
    prescriptions = appointment.prescriptions.all()

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.save()
            # Optionally, you can send the prescription added email here
            # send_prescription_email(appointment)
            return redirect('add_prescription', appointment_id=appointment_id)
    else:
        form = PrescriptionForm()

    return render(request, 'add_prescription.html', {'form': form, 'appointment': appointment, 'prescriptions': prescriptions})


def send_prescription_email(appointment):
    user_email = appointment.user.email
    subject = 'Prescription Added'
    message = 'Your prescription has been added. Please log in to view and download it.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    # Send the email
    send_mail(subject, message, from_email, recipient_list)
    


def view_patient_history(request, patient_id):
    # Assuming patient_id is the ID of the patient you want to view the history for
    patient = CustomUser.objects.get(pk=patient_id)
    appointments = Appointment.objects.filter(user=patient, doctor=request.user)  # Adjust this based on your actual User model structure
    
    prescription_history = Prescription.objects.filter(appointment__in=appointments)

    return render(request, 'view_patient_history.html', {'patient': patient, 'prescription_history': prescription_history})
# def view_prescription(request, appointment_id):
#     prescriptions = Prescription.objects.filter(appointment_id=appointment_id)
#     return render(request, 'view_prescription.html', {'prescriptions': prescriptions})


from django.shortcuts import render, get_object_or_404
from .models import Appointment, Prescription, ServiceSuggest

def view_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    prescriptions = Prescription.objects.filter(appointment=appointment)
    suggestions = ServiceSuggest.objects.filter(appointment=appointment)
    return render(request, 'view_prescription.html', {'prescriptions': prescriptions, 'suggestions': suggestions})


# def view_appointment_details(request, appointment_id):
#     appointment = Appointment.objects.get(pk=appointment_id)
#     payment = Payment.objects.get(appointment=appointment)
#     prescription = Prescription.objects.filter(appointment=appointment).first()

#     return render(request, 'appointment_details.html', {
#         'appointment': appointment,
#         'payment': payment,
#         'prescription': prescription,
#     })

@login_required
def view_appointment_details(request, appointment_id):
    # Assuming you have a user associated with the appointments
    user_appointments = Appointment.objects.filter(user=request.user)

    # Fetch the appointment after initializing other variables
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    # Fetch the payment for the appointment
    payment = Payment.objects.get(appointment=appointment)

    # Fetch the prescription for the appointment
    prescription = Prescription.objects.filter(appointment=appointment).first()

    return render(request, 'appointment_details.html', {
        'user_appointments': user_appointments,
        'payment': payment,
        'prescription': prescription,
        'appointment': appointment,
    })



# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from django.http import HttpResponse
# from .models import Appointment, Payment, Prescription
# from reportlab.lib import colors

# def download_prescription(request, appointment_id):
#     appointment = Appointment.objects.get(pk=appointment_id)
#     payment = Payment.objects.get(appointment=appointment)
#     prescriptions = Prescription.objects.filter(appointment=appointment)

#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="prescription_{appointment_id}.pdf"'

#     p = canvas.Canvas(response, pagesize=letter)

#     # Set font and font size
#     p.setFont("Helvetica", 12)

#     p.setFont("Helvetica-Bold", 16)
#     p.setFillColorRGB(0.2, 0.4, 0.8) 
#     p.setStrokeColorRGB(0.2, 0.4, 0.8)
#     p.drawCentredString(300, 800, "Simply Skin")  # Adjust the position as needed
#     # Add prescription details to the PDF
#     p.setFont("Helvetica", 12)
#     p.drawString(100, 750, f"Prescription for {appointment.user.get_full_name()}")
#     p.drawString(100, 730, f"Doctor: {appointment.user.get_full_name()}")
#     p.drawString(100, 710, f"Date: {appointment.date}")
#     p.drawString(100, 690, f"Time Slot: {appointment.time_slot}")
#     p.drawString(100, 670, f"Payment Method: {payment.method}")

#     # Iterate through prescriptions and add details to the PDF
#     y_position = 650  # Initial y position for prescription details
#     for prescription in prescriptions:
#         p.drawString(100, y_position, f"Medicine: {prescription.medicine}")
#         p.drawString(100, y_position - 20, f"Dosage: {prescription.dosage}")
#         p.drawString(100, y_position - 40, f"Duration: {prescription.duration}")
#         y_position -= 60  # Adjust y position for the next prescription

#     p.showPage()
#     p.save()

#     return response

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas

def download_prescription(request, appointment_id):
    appointment = Appointment.objects.get(pk=appointment_id)
    payment = Payment.objects.get(appointment=appointment)
    prescriptions = Prescription.objects.filter(appointment=appointment)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="prescription_{appointment_id}.pdf"'

    # Create a PDF document
    p = canvas.Canvas(response, pagesize=letter)

    # Set font and font size
    p.setFont("Helvetica", 12)

    # Draw the centered title
    title_text = "Simply Skin"
    title_font_size = 16
    title_x = letter[0] / 2  # X-coordinate for centering
    title_y = letter[1] - 50  # Y-coordinate from the top

    # Get the width of the title text
    title_width = p.stringWidth(title_text, 'Helvetica-Bold', title_font_size)

    # Calculate the X-coordinate to center the title
    title_x -= title_width / 2

    p.setFont("Helvetica-Bold", title_font_size)
    p.setFillColorRGB(0.2, 0.4, 0.8)
    p.drawCentredString(title_x, title_y, title_text)

    # Draw a line below the header for separation
    p.line(50, title_y - 10, letter[0] - 50, title_y - 10)

    # Calculate the starting point for the table
    table_starting_point = title_y - 280  # Adjusted to create space below the title

    # Create a list to hold table data
    table_data = [
        ["Prescription for", appointment.user.get_full_name()],
        ["Doctor",  appointment.doctor.first_name],
        ["Date", appointment.date],
        ["Time Slot", appointment.time_slot],
        ["Payment Method", payment.method],
    ]

    # Iterate through prescriptions and add details to the table
    for prescription in prescriptions:
        table_data.append(["Medicine", prescription.medicine])
        table_data.append(["Dosage", prescription.dosage])
        table_data.append(["Duration", prescription.duration])
        table_data.append(["", ""])  # Add an empty row for separation

    # Create the table and set styles
    table = Table(table_data, colWidths=[150, 200], style=[
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Get the width of the table
    table_width, table_height = table.wrap(0, 0)

    # Calculate the X-coordinate to center the table
    table_x = (letter[0] - table_width) / 2

    # Draw the table on the PDF
    table.drawOn(p, table_x, table_starting_point)

    p.showPage()
    p.save()

    return response



def view_more(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, user__id=doctor_id)

    return render(request, 'view_more.html', {'doctor': doctor})



from django.shortcuts import render
from .models import Appointment, Payment

def appointment_list(request):
    # Retrieve all appointments and related doctor and user information
    appointments = Appointment.objects.select_related('doctor_profile__user', 'user__userprofile').all()

    # Retrieve all payments related to appointments
    payments = Payment.objects.select_related('appointment__doctor_profile__user', 'appointment__user__userprofile').all()

    context = {
        'appointments': appointments,
        'payments': payments,
    }

    return render(request, 'appointment_li.html', context)


from django.shortcuts import render

def set_theme(request, theme):
    if theme in settings.AVAILABLE_THEMES:
        request.session['theme'] = theme
    return HttpResponse('Theme set successfully')


# views.py
from django.shortcuts import render, redirect
from .forms import BrandForm

def add_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('brand_list')  # Redirect to success page
    else:
        form = BrandForm()
    return render(request, 'add_brand.html', {'form': form})


def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'brand_list.html', {'brands': brands})


from .forms import CategoryForm
from .models import Category, Subcategory
def add_category(request):
    categories = Category.objects.all()  # Retrieve all categories
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            # Refresh the form to clear it for next entry
            form = CategoryForm()
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form, 'categories': categories})



from .forms import SubcategoryForm

def add_subcategory(request, category_id):
    category = Category.objects.get(pk=category_id)

    if request.method == 'POST':
        form = SubcategoryForm(request.POST)
        if form.is_valid():
            subcategory = form.save(commit=False)
            subcategory.category = category
            subcategory.save()
            return redirect('add_category')  # Redirect to the page where categories are listed
    else:
        form = SubcategoryForm()
    return render(request, 'add_subcategory.html', {'form': form, 'category': category})

def delete_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        category.delete()
    # Redirect back to the same page after deletion
    return redirect('add_category')

def whatsapp_chat(request, agent_phone):
    # Assuming the agent's WhatsApp number is passed as a parameter in the URL
    # You can add logic here to handle redirection to the WhatsApp chat page
    # For simplicity, let's assume you want to redirect to a WhatsApp URL
    whatsapp_url = f"https://wa.me/{agent_phone}"
    return redirect(whatsapp_url)

from django.shortcuts import render, redirect
from .forms import ProductForm
from .models import Brand, Category, Subcategory
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_date = timezone.now()  # Set the creation date
            product.save()
            form.save_m2m() 
            return redirect('product_list')  # Assuming you have a view named 'product_list' to redirect to
    else:
        form = ProductForm()
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    brand = Brand.objects.all()
    return render(request, 'add_product.html', {'form': form, 'categories': categories, 'subcategories': subcategories, 'brand': brand})






from .models import Product
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


# views.py
from django.http import JsonResponse
from .models import Subcategory

def get_subcategories(request, category_id):
    subcategories = Subcategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)



from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_list.html')

def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'update_product.html', {'form': form})

from django.shortcuts import render
from .models import Product, Wishlist
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static

# @login_required
# def display_product(request):
#     categories = Category.objects.all()
#     subcategories = Subcategory.objects.all()
#     selected_category = request.GET.get('category')
#     selected_subcategory = request.GET.get('subcategory')
#     user_profile, created = UserProfile.objects.get_or_create(user=request.user)
#     user_wishlist = Wishlist.objects.filter(user=request.user).first()  # Get the user's wishlist
#     products = Product.objects.all()
#     wishlist_icon = static('assets/img/wishlistred.png')
#     default_icon = static('assets/img/wishlist1.png')

#     if selected_subcategory:
#         products = Product.objects.filter(subcategory__name=selected_subcategory)
#     elif selected_category:
#         products = Product.objects.filter(subcategory__category__name=selected_category)

#     # Add a flag to each product indicating whether it's in the user's wishlist
#     for product in products:
#         product.in_wishlist = user_wishlist.products.filter(pk=product.pk).exists() if user_wishlist else False

#     return render(request, 'display_product.html', {'categories': categories, 'subcategories': subcategories, 'products': products,'wishlist_icon': wishlist_icon, 'default_icon': default_icon,'user_profile':user_profile})


@login_required
def display_product(request):
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    selected_category = request.GET.get('category')
    selected_subcategory = request.GET.get('subcategory')
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_wishlist = Wishlist.objects.filter(user=request.user).first()  
    cart_count = Cart.objects.filter(user=request.user).count()
    wishlist_icon = static('assets/img/wishlistred.png')
    default_icon = static('assets/img/wishlist1.png')

    # Check if there is a search query
    search_query = request.GET.get('q')
    if search_query:
        # Check if the search query matches any category
        matching_categories = Category.objects.filter(name__icontains=search_query)
        
        if matching_categories.exists():
            # Filter products based on categories matching the search query
            products = Product.objects.filter(subcategory__category__in=matching_categories)
        else:
            # Check if the search query matches any subcategory
            matching_subcategories = Subcategory.objects.filter(name__icontains=search_query)
            
            if matching_subcategories.exists():
                # Filter products based on subcategories matching the search query
                products = Product.objects.filter(subcategory__in=matching_subcategories)
            else:
                # Filter products based on the product name matching the search query
                products = Product.objects.filter(name__icontains=search_query)
    elif selected_subcategory:
        products = Product.objects.filter(subcategory__name=selected_subcategory)
    elif selected_category:
        products = Product.objects.filter(subcategory__category__name=selected_category)
    else:
        products = Product.objects.all()

    # Add a flag to each product indicating whether it's in the user's wishlist
    for product in products:
        product.in_wishlist = user_wishlist.products.filter(pk=product.pk).exists() if user_wishlist else False

    return render(request, 'display_product.html', {
        'categories': categories,
        'subcategories': subcategories,
        'products': products,
        'wishlist_icon': wishlist_icon,
        'default_icon': default_icon,
        'user_profile': user_profile,
        'cart_count': cart_count
    })

from django.shortcuts import render
from .models import Order, ShippingAddress, UserProfile

def bill_invoice(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        shipping_address = ShippingAddress.objects.filter(user=request.user, address_type='S').first()
        
        # Assuming there's a relationship between Order and Product through OrderItem
        products = order.orderitem_set.all()  # Get all order items related to this order
        product_names = [item.product.name for item in products]  # Get the names of all products
        
        # Assuming there's a one-to-one relationship between User and UserProfile
        user_profile = UserProfile.objects.get(user=request.user)
        phone_number = user_profile.phonenumber
        
    except Order.DoesNotExist:
        return render(request, 'error.html', {'error_message': 'Order not found'}, status=404)
    except ShippingAddress.DoesNotExist:
        shipping_address = None
    except UserProfile.DoesNotExist:
        phone_number = None

    context = {
        'order': order,
        'shipping_address': shipping_address,
        'product_names': product_names,
        'phone_number': phone_number,
    }
    return render(request, 'billinvoice.html', context)

from django.shortcuts import render

def whatsapp_chat(request, agent_phone):
    # Render the chat page template with the agent's phone number
    return render(request, 'chat_page.html', {'agent_phone': agent_phone})



def pharmacist_list(request):
    # Retrieve all pharmacist objects from the database
    pharmacists = CustomUser.objects.filter(role='pharmacist')

    # Pass the list of pharmacists to the template context
    context = {
        'pharmacists': pharmacists
    }

    # Render the template with the provided context
    return render(request, 'pharmacist-list.html', context)



from .models import Product, Cart, CartItem
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# @login_required(login_url='login')
# def add_to_cart(request, product_id):
#     product = Product.objects.get(pk=product_id)
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
#     if not item_created:
#         cart_item.quantity += 1
#         cart_item.save()
    
#     return redirect('cart')


@login_required(login_url='login')
def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))  # Get the quantity from the submitted form
        product = Product.objects.get(pk=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not item_created:
            if cart_item.quantity + quantity <= product.quality:  # Check if the total quantity doesn't exceed the product's quality
                cart_item.quantity += quantity
                cart_item.save()
            else:
                messages.warning(request, "Quantity cannot exceed available quality.")
        else:
            cart_item.quantity = quantity
            cart_item.save()

    return redirect('cart')


@login_required(login_url='login')
def remove_from_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    cart = Cart.objects.get(user=request.user)
    try:
        cart_item = cart.cartitem_set.get(product=product)
        if cart_item.quantity >= 1:
             cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    
    return redirect('cart')

# @login_required(login_url='login')
# def view_cart(request):
#     categories = Category.objects.all()
#     cart = request.user.cart
#     cart_items = CartItem.objects.filter(cart=cart)
#     return render(request, 'cart.html', {'cart_items': cart_items,'categories':categories})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Category, CartItem
from .utils import calculate_total_price  # Import the calculate_total_price function

@login_required(login_url='login')
def view_cart(request):
    categories = Category.objects.all()
    cart = request.user.cart
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Calculate total price
    total_price = calculate_total_price(request.user)
    
    return render(request, 'cart.html', {'cart_items': cart_items, 'categories': categories, 'total_price': total_price})


@login_required(login_url='login')
def increase_cart_item(request, product_id):
    product = Product.objects.get(pk=product_id)
    cart = request.user.cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if cart_item.quantity < product.quality:
        cart_item.quantity += 1
        cart_item.save()
        return redirect('cart')
    else:
        messages.warning(request, "Quantity cannot exceed available quality.")
        return redirect('cart')

@login_required(login_url='login')
def decrease_cart_item(request, product_id):
    product = Product.objects.get(pk=product_id)
    cart = request.user.cart
    cart_item = cart.cartitem_set.get(product=product)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')

@login_required(login_url='login')
def fetch_cart_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart = request.user.cart
        cart_count = CartItem.objects.filter(cart=cart).count()
    return JsonResponse({'cart_count': cart_count})


def get_cart_count(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart=request.user.cart)
        cart_count = cart_items.count()
    else:
        cart_count = 0
    return cart_count


from django.shortcuts import render, redirect
from .models import Product, Wishlist


@login_required
def wishlist(request):
    categories = Category.objects.all()
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'wishlist.html', {'wishlist': wishlist,'categories':categories})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    wishlist.products.remove(product)
    return redirect('wishlist')

from .models import  Product, Cart, CartItem, Order, OrderItem
from django.http import JsonResponse
from django.conf import settings
import razorpay
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        user = request.user
        cart = user.cart

        cart_items = CartItem.objects.filter(cart=cart)
        total_amount = sum(item.product.sale_price * item.quantity for item in cart_items)

        try:
            order = Order.objects.create(user=user, total_amount=total_amount)
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    item_total=cart_item.product.price * cart_item.quantity
                )

            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            payment_data = {
                'amount': int(total_amount * 100),
                'currency': 'INR',
                'receipt': f'order_{order.id}',
                'payment_capture': '1'
            }
            orderData = client.order.create(data=payment_data)
            order.payment_id = orderData['id']
            order.save()

            return JsonResponse({'order_id': orderData['id']})
        
        except Exception as e:
            print(str(e))
            return JsonResponse({'error': 'An error occurred. Please try again.'}, status=500)


# def checkout(request):
#     cart_items = CartItem.objects.filter(cart=request.user.cart)
#     total_amount = sum(item.product.price * item.quantity for item in cart_items)

#     cart_count = get_cart_count(request)
#     email = request.user.email
#     full_name = request.user.first_name

#     context = {
#         'cart_count': cart_count,
#         'cart_items': cart_items,
#         'total_amount': total_amount,
#         'email':email,
#         'full_name': full_name
#     }
#     return render(request, 'checkout.html', context)
        
# views.py
# views.py
from django.shortcuts import render, redirect
from .models import CartItem, ShippingAddress
from .forms import ShippingAddressForm
import pycountry

# def checkout(request):
#     cart_items = CartItem.objects.filter(cart=request.user.cart)
#     total_amount = sum(item.product.price * item.quantity for item in cart_items)

#     cart_count = get_cart_count(request)
#     email = request.user.email
#     full_name = request.user.first_name
    
#     shipping_addresses = ShippingAddress.objects.filter(user=request.user)
    
#     if request.method == 'POST':
#         address_id = request.POST.get('address_id')
#         if address_id:
#             address = ShippingAddress.objects.get(pk=address_id)
#             form = ShippingAddressForm(request.POST, instance=address)  # Initialize form with existing address instance
#             if form.is_valid():
#                 form.save()  # Save the updated address
#                 return redirect('checkout')
#         else:
#             form = ShippingAddressForm(request.POST)
#             if form.is_valid():
#                 shipping_address = form.save(commit=False)
#                 shipping_address.user = request.user
#                 shipping_address.address_type = 'S'
#                 shipping_address.save()
#                 return redirect('checkout')

#     else:
#         form = ShippingAddressForm()  # Use this line instead of initializing an empty form

#     countries = [(country.alpha_2, country.name) for country in pycountry.countries]
    

#     context = {
#         'cart_count': cart_count,
#         'cart_items': cart_items,
#         'total_amount': total_amount,
#         'email': email,
#         'full_name': full_name,
#         'form': form,
#         'shipping_addresses': shipping_addresses,
#         'countries': countries,
        
#     }
#     return render(request, 'checkout.html', context)



# from django.shortcuts import render, redirect
# from .models import Order
# from .forms import ShippingAddressForm
# import pycountry

# def checkout(request):
#     cart_items = CartItem.objects.filter(cart=request.user.cart)
#     total_amount = sum(item.product.sale_price * item.quantity for item in cart_items)

#     cart_count = get_cart_count(request)
#     email = request.user.email
#     full_name = request.user.first_name
    
#     shipping_addresses = ShippingAddress.objects.filter(user=request.user)
    
#     # Fetch the order if it exists
#     orders = Order.objects.filter(user=request.user, payment_status=True)
#     order = orders.first() if orders.exists() else None

#     if request.method == 'POST':
#         address_id = request.POST.get('address_id')
#         if address_id:
#             address = ShippingAddress.objects.get(pk=address_id)
#             form = ShippingAddressForm(request.POST, instance=address)
#             if form.is_valid():
#                 form.save()
#                 return redirect('checkout')
#         else:
#             form = ShippingAddressForm(request.POST)
#             if form.is_valid():
#                 shipping_address = form.save(commit=False)
#                 shipping_address.user = request.user
#                 shipping_address.address_type = 'S'
#                 shipping_address.save()
#                 return redirect('checkout')
#     else:
#         form = ShippingAddressForm()

#     countries = [(country.alpha_2, country.name) for country in pycountry.countries]
    
#     context = {
#         'cart_count': cart_count,
#         'cart_items': cart_items,
#         'total_amount': total_amount,
#         'email': email,
#         'full_name': full_name,
#         'form': form,
#         'shipping_addresses': shipping_addresses,
#         'countries': countries,
#         'order': order,
#     }
#     return render(request, 'checkout.html', context)from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ShippingAddress
from .forms import ShippingAddressForm
import pycountry

def checkout(request):
    cart_items = CartItem.objects.filter(cart=request.user.cart)
    total_amount = sum(item.product.sale_price * item.quantity for item in cart_items)

    cart_count = get_cart_count(request)
    email = request.user.email
    full_name = request.user.first_name
    
    shipping_address = ShippingAddress.objects.filter(user=request.user).first()
    form = ShippingAddressForm(instance=shipping_address)
    
    countries = [(country.alpha_2, country.name) for country in pycountry.countries]
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, 'Shipping address updated successfully!')
            return redirect('checkout')
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'cart_count': cart_count,
        'cart_items': cart_items,
        'total_amount': total_amount,
        'email': email,
        'full_name': full_name,
        'form': form,
        'shipping_address': shipping_address,
        'countries': countries,
    }
    return render(request, 'checkout.html', context)




def delete_address(request, address_id):
    address = get_object_or_404(ShippingAddress, pk=address_id)
    address.delete()
    return redirect('checkout')  # Redirect to the checkout page after deletion
@csrf_exempt
def handle_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        razorpay_order_id = data.get('order_id')
        payment_id = data.get('payment_id')

        try:
            order = Order.objects.get(payment_id=razorpay_order_id)

            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            payment = client.payment.fetch(payment_id)

            if payment['status'] == 'captured':
                order.payment_status = True
                order.save()
                user = request.user
                user.cart.cartitem_set.all().delete()
                return JsonResponse({'message': 'Payment successful'})
            else:
                return JsonResponse({'message': 'Payment failed'})

        except Order.DoesNotExist:
            return JsonResponse({'message': 'Invalid Order ID'})
        except Exception as e:

            print(str(e))
            return JsonResponse({'message': 'Server error, please try again later.'})
        






    # If form is not valid or if the request method is not POST, redirect back to checkout
    return redirect('checkout')

# views.py

from django.shortcuts import render
from .models import Order

def order_summary(request):
    orders = Order.objects.all()
    context = {'orders': orders}
    return render(request, 'order_summary.html', context)



from django.shortcuts import render, get_object_or_404
from .models import Product

def product_details(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    selected_category = request.GET.get('category')
    selected_subcategory = request.GET.get('subcategory')
    return render(request, 'product_details.html', {'product': product, 'categories': categories, 'subcategories': subcategories,'selected_category':selected_category,' selected_subcategory': selected_subcategory})



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import CartItem

def update_cart_item(request):
    if request.method == 'POST' and request.is_ajax():
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        cart_item = get_object_or_404(CartItem, product_id=product_id, cart__user=request.user)
        cart_item.quantity = quantity
        cart_item.save()

        # Calculate total price and return it in the response
        total_price = calculate_total_price(request.user)
        return JsonResponse({'total_price': total_price})

    # If the request is not AJAX or not POST, return an error response
    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.shortcuts import render, get_object_or_404
from .models import Order

def bill_invoice(request):
    # Fetch the latest order for the logged-in user (or implement your logic)
    order = Order.objects.filter(user=request.user).latest('created_at')
    return render(request, 'billinvoice.html', {'order': order})

from django.shortcuts import render
from .models import Product

def search_products(request):
    query = request.GET.get('query')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.none()
    return render(request, 'search_results.html', {'products': products})


# views.py

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from django.conf import settings
from .models import DeliveryUser

def deliveryregister(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        username = request.POST.get('username')
        
        # Generate a random password
        generated_password = get_random_string(length=10)
        
        # Save the password hash
        hashed_password = make_password(generated_password)

        # Create a new user
        new_user = DeliveryUser(name=name, email=email, phone_number=phone_number, username=username, password=hashed_password)
        new_user.save()

        # Send the password to the user's email
        send_mail(
            'Your Password',
            f'Hello {username}, your generated password is: {generated_password}',
            settings.DEFAULT_FROM_EMAIL,  # Use the default sender email
            [email],  # Send email to the user's email address
            fail_silently=False,
        )

        return redirect('login')  # Redirect to login page after successful registration

    return render(request, 'deliveryregister.html')


# views.py
from django.shortcuts import redirect, get_object_or_404
from .models import Appointment

def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment.delete()
        # Redirect to some page after deletion, maybe back to the doctor's dashboard
        return redirect('doctor_dashboard')
    # Handle if the request method is not POST (optional)
    return redirect('doctor_dashboard')

def delete_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, pk=prescription_id)
    prescription.delete()
    return redirect('add_prescription', appointment_id=prescription.appointment.id)

from django.shortcuts import render, redirect
from .forms import ServiceForm,ServiceSuggestForm

def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('services_list')  # Replace 'home' with the name of your home URL pattern
    else:
        form = ServiceForm()
    return render(request, 'add_service.html', {'form': form})


from django.urls import reverse

def suggest_service(request, appointment_id):
    if request.method == 'POST':
        form = ServiceSuggestForm(request.POST)
        if form.is_valid():
            service_suggest = form.save(commit=False)
            service_suggest.appointment_id = appointment_id
            service_suggest.save()
            # Redirect to the same view after form submission
            return redirect('suggest_service', appointment_id=appointment_id)
    else:
        form = ServiceSuggestForm()
    return render(request, 'suggest_service.html', {'form': form})


from .models import Service

def service_list(request):
    services = Service.objects.all()
    return render(request, 'services.html', {'services': services})

# from django.shortcuts import render, redirect
# from .models import Booking

# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Service

# def book_service(request, service_id):
#     if request.method == 'POST':
#         user_id = request.user.id 
#         date = request.POST.get('date')
#         time_slot = request.POST.get('time_slot')

#         # Retrieve the Service object or return 404 if not found
#         service = get_object_or_404(Service, pk=service_id)

#         # Assuming you have a CustomUser model for users
#         # Replace this with your actual user model if different
#         user = CustomUser.objects.get(pk=user_id)

#         # Assuming you have a Booking model to store bookings
#         # Replace this with your actual Booking model
#         booking = Booking.objects.create(service=service, user=user, date=date, time_slot=time_slot)
#         return redirect('booking_success', booking_id=booking.id)

#     # If it's not a POST request, just render the template with the service_id
#     # You might want to pass the service details to the template as well if needed
#     return render(request, 'book_service.html', {'service_id': service_id})


# from django.shortcuts import render
# from django.http import HttpResponseRedirect
# from .models import Service, TimeSlot, Booking

# def book_service(request, service_id):
#     if request.method == 'POST':
#         # Retrieve data from the form
#         date = request.POST.get('date')
#         selected_time_slot = request.POST.get('time_slot')

#         # Save the booking
#         service = Service.objects.get(pk=service_id)
#         user = request.user  # Assuming you have authentication configured
#         booking = Booking(service=service, user=user, date=date, time_slot=selected_time_slot)
#         booking.save()

#         # Redirect to some confirmation page
#         return HttpResponseRedirect(reverse('booking_success'))   # Replace '/confirmation/' with your desired URL

#     else:
#         # Get the selected service
#         service = Service.objects.get(pk=service_id)
#         # Get all available time slots for the selected service
#         time_slots = TimeSlot.objects.filter(service=service)

#         return render(request, 'book_service.html', {'service': service, 'time_slots': time_slots})


# def booking_success(request, booking_id):
#     booking = Booking.objects.get(pk=booking_id)
#     return render(request, 'booking_success.html', {'booking': booking})



from django.shortcuts import render, redirect
from .models import Booking, Payment

from django.conf import settings
import razorpay

def booking_success(request, booking_id):
    booking = Booking.objects.get(pk=booking_id)
    
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        if razorpay_payment_id:
            # Payment is successful, update booking status and create payment record
            booking.status = 'paid'
            booking.save()

            # Create payment record
            payment = Payment.objects.create(
                service=booking.service,
                user=request.user,  # Assuming user is logged in
                amount=booking.service.advance_payment,
                payment_id=razorpay_payment_id,
                payment_status=Payment.COMPLETE
            )
            
            return redirect('booking_success', booking_id=booking.id)
        else:
            # Payment failed or not completed
            # You can handle this case as per your requirement, maybe show an error message
            pass
    
    context = {
        'booking': booking,
        'razorpay_key': settings.RAZOR_KEY_ID, # Assuming you have defined RAZORPAY_KEY in your settings.py
        'amount': int(booking.service.advance_payment * 100), # Amount in paise
    }
    return render(request, 'booking_success.html', context)


# from django.shortcuts import render, redirect
# from .models import Booking, Payment

# from django.conf import settings
# import razorpay

# def booking_success(request, booking_id):
#     booking = Booking.objects.get(pk=booking_id)
    
#     if request.method == 'POST':
#         razorpay_payment_id = request.POST.get('razorpay_payment_id')
#         if razorpay_payment_id:
#             # Payment is successful, update booking status and create payment record
#             booking.status = 'paid'
#             booking.save()

#             # Create payment record
#             payment = Payment.objects.create(
#                 service=booking.service,
#                 user=request.user,  # Assuming user is logged in
#                 amount=booking.service.advance_payment,
#                 payment_id=razorpay_payment_id,
#                 payment_status=Payment.COMPLETE
#             )
#             payment.save()
            
#             return redirect('booking_success', booking_id=booking.id)
#         else:
#             # Payment failed or not completed
#             # You can handle this case as per your requirement, maybe show an error message
#             pass
    
#     context = {
#         'booking': booking,
#         'razorpay_key': settings.RAZOR_KEY_ID, # Assuming you have defined RAZORPAY_KEY in your settings.py
#         'amount': int(booking.service.advance_payment * 100), # Amount in paise
#     }
#     return render(request, 'booking_success.html', context)

from .models import Service

def services_list(request):
    services = Service.objects.all()
    return render(request, 'services_list.html', {'services': services})



# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import TimeSlot

def add_time_slot(request, service_id):
    if request.method == 'POST':
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        
        # Check if a time slot with the same date and time already exists
        existing_time_slot = TimeSlot.objects.filter(date=date, time_slot=time_slot).exists()
        if existing_time_slot:
            messages.error(request, 'This time slot already exists for the selected date.')
            return redirect('add_time_slot', service_id=service_id)
        
        # If the time slot doesn't exist, create a new one
        new_time_slot = TimeSlot(date=date, time_slot=time_slot, service_id=service_id)
        new_time_slot.save()
        
        messages.success(request, 'Time slot added successfully.')
        return redirect('add_time_slot', service_id=service_id)
    
    else:
        # Render the form template
        time_slots = TimeSlot.objects.all()
        return render(request, 'add_time_slot.html', {'time_slots': time_slots})

# views.py

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import TimeSlot

def delete_time_slot(request, time_slot_id):
    # Attempt to retrieve the TimeSlot object with the given time_slot_id
    time_slot = get_object_or_404(TimeSlot, pk=time_slot_id)
    
    try:
        # Store the service_id before deleting the time slot
        service_id = time_slot.service_id  
    
        # Delete the time slot
        time_slot.delete()
        
        # Display a success message
        messages.success(request, 'Time slot deleted successfully.')
        
        # Redirect to the page where the time slots are listed, passing the service_id
        return redirect('add_time_slot', service_id=service_id)
    
    except Exception as e:
        # Display an error message if there's any issue with deleting the time slot
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('add_time_slot', service_id=service_id)

from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Service

@require_POST
def delete_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    service.delete()
    return redirect('services_list')  # Redirect to the service list page after deletion

# from django.shortcuts import render
# from django.http import HttpResponseRedirect, JsonResponse
# from django.urls import reverse  # Import reverse function

# from .models import Service, TimeSlot, Booking

# def book_service(request, service_id):
#     if request.method == 'POST':
#         # Retrieve data from the form
#         date = request.POST.get('date')
#         selected_time_slot = request.POST.get('time_slot')

#         # Save the booking
#         service = Service.objects.get(pk=service_id)
#         user = request.user  # Assuming you have authentication configured
#         booking = Booking(service=service, user=user, date=date, time_slot=selected_time_slot)
#         booking.save()

#         # Retrieve the ID of the newly created booking instance
#         booking_id = booking.id

#         # Redirect to booking success page with the booking ID
#         return HttpResponseRedirect(reverse('booking_success', args=[booking_id]))

#     else:
#         # Get the selected service
#         service = Service.objects.get(pk=service_id)
#         # Get all available time slots for the selected service
#         time_slots = TimeSlot.objects.filter(service=service)

#         return render(request, 'book_service.html', {'service': service, 'time_slots': time_slots})

def get_time_slots(request):
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        service_id = request.GET.get('service_id')
        time_slots = TimeSlot.objects.filter(date=selected_date, service_id=service_id).values('time_slot')
        return JsonResponse(list(time_slots), safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method'})

from django.db.models import Exists, OuterRef

# def get_time_slots(request):
#     if request.method == 'GET':
#         selected_date = request.GET.get('date')
#         service_id = request.GET.get('service_id')
        
#         # Update this query to annotate each time slot with a 'booked' flag
#         time_slots = TimeSlot.objects.filter(date=selected_date, service_id=service_id).annotate(
#             booked=Exists(
#                 Booking.objects.filter(
#                     time_slot_id=OuterRef('pk'),
#                     date=selected_date,
#                     service_id=service_id
#                 )
#             )
#         ).values('id', 'time_slot', 'booked')  # Ensure to include 'booked' in the values call
        
#         return JsonResponse(list(time_slots), safe=False)
#     else:
#         return JsonResponse({'error': 'Invalid request method'})

# views.py



from django.shortcuts import render, get_object_or_404
from .models import Service

def service_detail(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    return render(request, 'service_details.html', {'service': service})


from django.shortcuts import render
from .models import Product

def product_admin(request):
    products = Product.objects.all()
    return render(request, 'product_admin.html', {'products': products})

from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Service, TimeSlot, Booking

def book_service(request, service_id):
    if request.method == 'POST':
        # Retrieve data from the form
        date = request.POST.get('date')
        selected_time_slot = request.POST.get('time_slot')

        # Save the booking
        service = Service.objects.get(pk=service_id)
        user = request.user  # Assuming you have authentication configured
        booking = Booking(service=service, user=user, date=date, time_slot=selected_time_slot)
        booking.save()

         # Retrieve the ID of the newly created booking instance
        booking_id = booking.id

#         # Redirect to booking success page with the booking ID
        return HttpResponseRedirect(reverse('booking_success', args=[booking_id]))
    else:
        # Get the selected service
        service = Service.objects.get(pk=service_id)
        # Get all available time slots for the selected service
        time_slots = TimeSlot.objects.filter(service=service)

        return render(request, 'book_service.html', {'service': service, 'time_slots': time_slots})


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Service, TimeSlot, Booking
from django.http import HttpResponseRedirect
from datetime import datetime

# def book_service(request, service_id):
#     service = Service.objects.get(pk=service_id)
#     return render(request, 'book_service.html', {'service': service})

@require_POST
def get_time_slots(request):
    date = request.POST.get('date')
    service_id = request.POST.get('service_id')
    
    # Assuming you have a ForeignKey relationship between Service and TimeSlot
    time_slots = TimeSlot.objects.filter(service_id=service_id, date=date)
    
    # Check if any time slots are already booked for the selected date
    booked_time_slots = Booking.objects.filter(service_id=service_id, date=date).values_list('time_slot', flat=True)
    
    available_time_slots = []
    for time_slot in time_slots:
        # Check if the time slot is already booked
        is_booked = time_slot.time_slot in booked_time_slots
        available_time_slots.append({
            'time_slot': time_slot.time_slot,
            'is_booked': is_booked
        })
    
    return JsonResponse(available_time_slots, safe=False)

# @require_POST
# def book_time_slot(request):
#     service_id = request.POST.get('service_id')
#     date = request.POST.get('date')
#     time_slot = request.POST.get('time_slot')
    
#     # Assuming you have authentication configured
#     user = request.user  
    
#     # Save the booking
#     service = Service.objects.get(pk=service_id)
#     booking = Booking(service=service, user=user, date=date, time_slot=time_slot)
#     booking.save()

#     # Redirect to booking success page
#     return HttpResponseRedirect(reverse('booking_success'))  # Replace 'booking_success' with your actual URL name



# @csrf_exempt
# def chatgpt(request):
#     return render(request, 'chatgpt.html')


# from django.shortcuts import render
# from django.http import JsonResponse

# def generate_response(request):
#     if request.method == 'POST':
#         user_input = request.POST.get('user_input').lower()
#         if 'simplyskin' in user_input:
#             response_data = {'response': "Simplyskin make Healthier the skin, better the lifestyle ! How can I assist you today?"}
#         elif 'brand' in user_input:
#             # Get all brand names from the database
#             brand_names = Brand.objects.values_list('brand_name', flat=True)
#             # Convert queryset to list
#             brand_list = list(brand_names)
#             # Format response with brand names
#             brand_response = ", ".join(brand_list)
#             response_data = {'response': f"Here are the brand names: {brand_response}"}
#         elif 'products' in user_input:
#              response_data = {
#         'response': "We offer a wide range of skin care products. <a href='/display_product/'>Browse our collection online!</a>" }
#         elif 'product' in user_input:
#              response_data = {
#         'response': "We offer a wide range of skin care products. <a href='/display_product/'>Browse our collection online!</a>" }
#         elif 'doctor' in user_input:
#             response_data = {
#                 'response': "Looking to book an appointment with a doctor? Click here <a href='/appointment.html'>here</a> to schedule your visit!"}
#         elif 'hi' in user_input:
#             response_data = {'response': "hellooo"}
#         elif 'hairfall' in user_input or 'hair' in user_input:
#             response_data = {'response': "Struggling with hairfall? Explore our range of products specifically designed to target HairFall. <a href='/display_product/'>Browse now!</a>"}
#         elif 'acne' in user_input:
#             response_data = {'response': "Struggling with acne? Explore our range of products specifically designed to target acne-prone skin. <a href='/display_product/'>Browse now!</a>"}
#         elif 'skincare for oily skin' in user_input:
#             response_data = {'response': "For oily skin, we recommend starting with a gentle cleanser, followed by a toner to balance oil production. Consider using a lightweight, oil-free moisturizer and a mattifying sunscreen during the day."}
#         elif 'doctor' in user_input or 'appointment' in user_input:
#             # Redirect to appointment page
#             return redirect('appointment')
#         elif 'doctor' in user_input or 'appointment' in user_input:
#             response_data = {'response': "Looking to book an appointment with a doctor? Click <a href='/appointment/'>here</a> to schedule your visit!"}
#         elif 'return policy' in user_input:
#             response_data = {'response': "We want you to be satisfied with your purchase! Our return policy allows for returns within 30 days of delivery."}
#         elif 'offers' in user_input or 'discounts' in user_input:
#             response_data = {'response': "Check out our latest offers and discounts on premium beauty products. Don't miss out on great deals!"}
#         elif 'order' in user_input or 'delivery' in user_input:
#             response_data = {'response': "For information about your order or delivery, please contact our customer support at support@simplyskin.com."}
#         elif ' acnetreatment' in user_input or 'suggest acne treatment' in user_input:
#             response_data = {'response': "The best treatment for acne is HydraFacial. It deeply cleanses, exfoliates, and hydrates the skin, reducing acne and improving overall skin health. You can learn more about HydraFacial and other services <a href='/service_list/'>here</a>."}
       
#         else:
#             response_data = {'response': "Sorry, I don't understand."}

#         return JsonResponse(response_data)
#     else:
#         return JsonResponse({'error': 'Invalid request method'})

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login
from django.conf import settings
from .forms import DeliveryBoyRegistrationForm

def register_delivery_boy(request):
    if request.method == 'POST':
        form = DeliveryBoyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Send email with autogenerated password
            subject = 'Your DeliveryBoy Account Information'
            message = render_to_string('email.html', {
                'user': user,
                'password': user.password,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            # Log the user in with autogenerated password
            authenticated_user = authenticate(username=user.username, password=user.password)
            if authenticated_user:
                login(request, authenticated_user)
                return redirect('indexadmin')  # Redirect to home page after login
    else:
        form = DeliveryBoyRegistrationForm()
    return render(request, 'register_delivery_boy.html', {'form': form})


# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message

@login_required
def chat_room(request):
    user = request.user
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Create a new message
            message = Message.objects.create(sender=user, receiver=user, content=content)
            # Redirect to prevent form resubmission on page refresh
            return redirect('chat_room')

    # Retrieve messages sent and received by the user
    chats_sent = Message.objects.filter(sender=user).order_by('-timestamp')
    chats_received = Message.objects.filter(receiver=user).order_by('-timestamp')

    context = {
        'user': user,
        'chats_sent': chats_sent,
        'chats_received': chats_received,
    }
    return render(request, 'chat_room.html', context)


from django.shortcuts import render
from .models import Order

def available_orders(request):
    # Query the database for all orders
    all_orders = Order.objects.all()

    # Pass all_orders data to the template
    return render(request, 'availableorders.html', {'available_orders':all_orders})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
import random
import logging

logger = logging.getLogger(__name__)




@login_required(login_url='login')
def delivery_update_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        delivery_status = request.POST.get('delivery_status')

        if delivery_status == 'Delivered':
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            send_mail(
                'Delivery Confirmation OTP',
                f'Your OTP for order {order.id} is: {otp}',
                settings.EMAIL_HOST_USER,
                [order.user.email],
                fail_silently=False,
            )

            # Store OTP and order ID in session for later verification
            request.session['delivery_status_otp'] = otp
            request.session['otp_order_id'] = str(order_id)

            messages.info(request, 'OTP has been sent to the customer for delivery confirmation.')
            return redirect('otp_verification', order_id=order_id)  # Redirect to OTP verification page with order_id

        else:
            order.delivery_status = delivery_status
            order.save()
            messages.success(request, 'Delivery status updated successfully.')
            return redirect('available_orders')  # Redirect to the delivery boy dashboard

    return render(request, "deliveryupdatestatus.html", {'order': order})

@login_required(login_url='login')
def otp_verification(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        submitted_otp = request.POST.get('otp')
        session_order_id = request.session.get('otp_order_id')

        if str(order_id) == session_order_id and submitted_otp == request.session.get('delivery_status_otp'):
            # OTP is correct, update the delivery status
            order.delivery_status = 'Delivered'
            order.save()

            # Clear OTP and order ID from session
            del request.session['delivery_status_otp']
            del request.session['otp_order_id']

            # Redirect to a success page or the delivery details page
            messages.success(request, 'Order marked as delivered successfully.')
            return redirect('available_orders')
        else:
            # OTP is incorrect, render the OTP verification page with error message
            messages.error(request, 'Incorrect OTP. Please try again.')
            return render(request, 'otp_verification.html', {'order': order, 'error_message': 'Incorrect OTP. Please try again.'})

    else:
        return render(request, 'otp_verify.html', {'order':order})