
from django.contrib import admin
from django.urls import path, include
from hospital_app import views

urlpatterns = [
    

   

    # Home 
    path( '', views.home, name='home' ),
    # Authentication 
    path( 'login/', views.login_view, name='login' ), 
    path( 'signup/', views.signup_view, name='signup' ),
    path( 'logout/', views.logout_view, name='logout' ), 
    # Dashboard 
    path( 'dashboard/', views.dashboard, name='dashboard' ), 
    # Hospital information
     path( 'departments/', views.departments, name='departments' ), 
     path( 'doctors/', views.doctors, name='doctors' ), 
     path( 'patients/', views.patients, name='patients' ), 
     # Version 2 - Appointments 
     path( 'book-appointment/', views.book_appointment, name='book_appointment' ), 
     path( 'appointment-success/<int:appointment_id>/', views.appointment_success, name='appointment_success' ), 
     path( 'my-appointments/', views.my_appointments, name='my_appointments' ), 
     
     ]

