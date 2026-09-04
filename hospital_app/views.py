
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError

from .models import (
    Department,
    Doctor,
    Patient,
    Profile,
    Appointment,
)


# =========================
# HOME
# =========================

def home(request):
    return render(
        request,
        'home.html'
    )


# =========================
# DEPARTMENTS
# =========================

def departments(request):

    departments = Department.objects.all()

    return render(
        request,
        'hospital_app/departments.html',
        {
            'departments': departments
        }
    )


# =========================
# DOCTORS
# =========================

def doctors(request):

    doctors = Doctor.objects.select_related(
        'user',
        'department'
    )

    return render(
        request,
        'hospital_app/doctors.html',
        {
            'doctors': doctors
        }
    )


# =========================
# PATIENTS
# =========================

@login_required
def patients(request):

    patients = Patient.objects.filter(
        user=request.user
    )

    return render(
        request,
        'hospital_app/patients.html',
        {
            'patients': patients
        }
    )


# =========================
# LOGIN
# =========================

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')

        matching_users = User.objects.filter(
            username__iexact=username
        )

        if not matching_users.exists() and '@' in username:
            matching_users = User.objects.filter(
                email__iexact=username
            )

        user = None
        for matching_user in matching_users:
            user = authenticate(
                request,
                username=matching_user.username,
                password=password
            )
            if user is not None:
                break

        if user is None:
            user = authenticate(
                request,
                username=username,
                password=password
            )

        if user is not None:

            login(request, user)

            if user.is_superuser:
                return redirect('dashboard')

            try:

                Profile.objects.get(
                    user=user
                )

                return redirect('dashboard')

            except Profile.DoesNotExist:

                return redirect('home')

        else:

            return render(
                request,
                'hospital_app/login.html',
                {
                    'error': 'Invalid username or password',
                    'username': username
                }
            )

    return render(
        request,
        'hospital_app/login.html'
    )


# =========================
# SIGNUP
# =========================

def signup_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    form_data = request.POST if request.method == 'POST' else {}
    errors = []

    if request.method == 'POST':

        username = form_data.get('username', '').strip()
        first_name = form_data.get('first_name', '').strip()
        last_name = form_data.get('last_name', '').strip()
        email = form_data.get('email', '').strip()
        password = form_data.get('password', '')
        password_confirmation = form_data.get('password_confirmation', '')
        age_value = form_data.get('age', '').strip()
        phone = form_data.get('phone', '').strip()
        address = form_data.get('address', '').strip()

        if User.objects.filter(username__iexact=username).exists():
            errors.append('That username is already in use.')

        if password != password_confirmation:
            errors.append('The passwords do not match.')

        try:
            validate_password(password, user=User(username=username))
        except ValidationError as validation_error:
            errors.extend(validation_error.messages)

        try:
            age = int(age_value)
            if age < 1 or age > 120:
                raise ValueError
        except (TypeError, ValueError):
            errors.append('Enter an age between 1 and 120.')

        if not phone:
            errors.append('Enter a phone number.')

        if not address:
            errors.append('Enter your address.')

        if not errors:
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password
                    )
                    Profile.objects.create(user=user, role='Patient')
                    Patient.objects.create(
                        user=user,
                        age=age,
                        phone=phone,
                        address=address
                    )
            except IntegrityError:
                errors.append('That username is already in use.')
            else:
                login(request, user)
                return redirect('dashboard')

    return render(
        request,
        'hospital_app/signup.html',
        {
            'errors': errors,
            'form_data': form_data
        }
    )


# =========================
# DASHBOARD
# =========================

@login_required
def dashboard(request):

    # Admin dashboard
    if request.user.is_superuser:

        return render(
            request,
            'hospital_app/admin_dashboard.html'
        )

    try:

        profile = Profile.objects.get(
            user=request.user
        )

        # Doctor dashboard
        if profile.role == 'Doctor':

            doctor = Doctor.objects.get(
                user=request.user
            )

            return render(
                request,
                'hospital_app/doctor_dashboard.html',
                {
                    'doctor': doctor
                }
            )

        # Patient dashboard
        elif profile.role == 'Patient':

            patient = Patient.objects.get(
                user=request.user
            )

            return render(
                request,
                'hospital_app/patient_dashboard.html',
                {
                    'patient': patient
                }
            )

    except (
        Profile.DoesNotExist,
        Doctor.DoesNotExist,
        Patient.DoesNotExist
    ):

        return redirect('home')

    return redirect('home')


# =========================
# LOGOUT
# =========================

def logout_view(request):

    logout(request)

    return redirect('home')


# =========================
# BOOK APPOINTMENT
# =========================

@login_required
def book_appointment(request):

    doctors = Doctor.objects.select_related(
        'user',
        'department'
    )

    if request.method == 'POST':

        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get(
            'appointment_date'
        )
        appointment_time = request.POST.get(
            'appointment_time'
        )

        # Basic validation
        if not doctor_id:
            return render(
                request,
                'book_appointment.html',
                {
                    'doctors': doctors,
                    'error': 'Please select a doctor.'
                }
            )

        if not appointment_date:
            return render(
                request,
                'book_appointment.html',
                {
                    'doctors': doctors,
                    'error': 'Please select an appointment date.'
                }
            )

        if not appointment_time:
            return render(
                request,
                'book_appointment.html',
                {
                    'doctors': doctors,
                    'error': 'Please select an appointment time.'
                }
            )

        doctor = get_object_or_404(
            Doctor,
            id=doctor_id
        )

        # Check whether the slot is already booked
        existing = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='Booked'
        ).exists()

        if existing:

            return render(
                request,
                'book_appointment.html',
                {
                    'doctors': doctors,
                    'error':
                    'This doctor is already booked for this time slot.'
                }
            )

        try:

            with transaction.atomic():

                appointment = Appointment.objects.create(
                    patient=request.user,
                    doctor=doctor,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    status='Booked'
                )

            return redirect(
                'appointment_success',
                appointment_id=appointment.id
            )

        except IntegrityError:

            return render(
                request,
                'book_appointment.html',
                {
                    'doctors': doctors,
                    'error':
                    'This doctor is already booked for this time slot.'
                }
            )

    return render(
        request,
        'book_appointment.html',
        {
            'doctors': doctors
        }
    )


# =========================
# APPOINTMENT SUCCESS
# =========================

@login_required
def appointment_success(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=request.user
    )

    return render(
        request,
        'appointment_success.html',
        {
            'appointment': appointment
        }
    )


# =========================
# MY APPOINTMENTS
# =========================

@login_required
def my_appointments(request):

    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by(
        '-appointment_date',
        '-appointment_time'
    )

    return render(
        request,
        'my_appointments.html',
        {
            'appointments': appointments
        }
    )

