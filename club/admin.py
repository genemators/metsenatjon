from django.contrib import admin
from .models import Sponsor, Student, Donation

admin.site.register(Sponsor)
admin.site.register(Student)
admin.site.register(Donation)