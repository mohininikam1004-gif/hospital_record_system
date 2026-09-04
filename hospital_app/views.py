
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction

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

        username = request.POST.get('username')
        password = request.POST.get('password')

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
                    'error': 'Invalid username or password'
                }
            )

    return render(
        request,
        'hospital_app/login.html'
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
                'hospital_app/book_appointment.html',
                {
                    'doctors': doctors,
                    'error': 'Please select a doctor.'
                }
            )

        if not appointment_date:
            return render(
                request,
                'hospital_app/book_appointment.html',
                {
                    'doctors': doctors,
                    'error': 'Please select an appointment date.'
                }
            )

        if not appointment_time:
            return render(
                request,
                'hospital_app/book_appointment.html',
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
                'hospital_app/book_appointment.html',
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
                'hospital_app/book_appointment.html',
                {
                    'doctors': doctors,
                    'error':
                    'This doctor is already booked for this time slot.'
                }
            )

    return render(
        request,
        'hospital_app/book_appointment.html',
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
        'hospital_app/appointment_success.html',
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
        'hospital_app/my_appointments.html',
        {
            'appointments': appointments
        }
    )

