from django.contrib import admin
from .models import Classroom, SchoolSettings, Student, StudentAttendance, TeacherAttendance

admin.site.register(SchoolSettings)
admin.site.register(Classroom)
admin.site.register(Student)
admin.site.register(StudentAttendance)
admin.site.register(TeacherAttendance)
