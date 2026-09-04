from django.contrib import admin
from .models import Department, Profile, Doctor, Patient


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'department',
        'specialization',
        'phone'
    )


from django.contrib import admin
from .models import Appointment

admin.site.register(Appointment)