from datetime import date
from decimal import Decimal
from math import asin, cos, radians, sin, sqrt

from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

FIXED_SCHOOL_LATITUDE = Decimal('41.08022969852711')
FIXED_SCHOOL_LONGITUDE = Decimal('69.04543362274605')
FIXED_ALLOWED_RADIUS_METERS = 120


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SchoolSettings(models.Model):
    school_name = models.CharField(max_length=255, default='My School')
    latitude = models.DecimalField(max_digits=18, decimal_places=14, default=FIXED_SCHOOL_LATITUDE)
    longitude = models.DecimalField(max_digits=18, decimal_places=14, default=FIXED_SCHOOL_LONGITUDE)
    allowed_radius_meters = models.PositiveIntegerField(default=FIXED_ALLOWED_RADIUS_METERS)
    work_start_time = models.TimeField(default='08:00')
    work_end_time = models.TimeField(default='17:00')
    late_after_minutes = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.school_name

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        changed = False
        if obj.latitude != FIXED_SCHOOL_LATITUDE:
            obj.latitude = FIXED_SCHOOL_LATITUDE
            changed = True
        if obj.longitude != FIXED_SCHOOL_LONGITUDE:
            obj.longitude = FIXED_SCHOOL_LONGITUDE
            changed = True
        if obj.allowed_radius_meters != FIXED_ALLOWED_RADIUS_METERS:
            obj.allowed_radius_meters = FIXED_ALLOWED_RADIUS_METERS
            changed = True
        if changed:
            obj.save(update_fields=['latitude', 'longitude', 'allowed_radius_meters'])
        return obj


class Classroom(TimeStampedModel):
    SHIFT_MORNING = 'morning'
    SHIFT_AFTERNOON = 'afternoon'
    SHIFT_CHOICES = [
        (SHIFT_MORNING, 'Ertalab'),
        (SHIFT_AFTERNOON, 'Abetdan keyin'),
    ]

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classrooms')
    name = models.CharField(max_length=120)  # Sinf nomi
    grade_level = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=100, blank=True, default='')
    room = models.CharField(max_length=50, blank=True)  # Xona
    lesson_time = models.CharField(max_length=50, blank=True)  # Dars vaqti, masalan 08:00-10:00
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default=SHIFT_MORNING)  # Ertalab / Abetdan keyin
    schedule_info = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('teacher', 'name', 'subject')
        ordering = ['name']

    def __str__(self):
        subject = f" - {self.subject}" if self.subject else ''
        return f"{self.name}{subject}"


class Student(TimeStampedModel):
    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    GENDER_CHOICES = [
        (GENDER_MALE, 'Erkak'),
        (GENDER_FEMALE, 'Ayol'),
    ]

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='students')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_primary = models.CharField(max_length=20, blank=True)  # O'quvchi nomeri
    phone_secondary = models.CharField(max_length=20, blank=True)
    parent_name = models.CharField(max_length=150, blank=True)
    father_full_name = models.CharField(max_length=150, blank=True)
    father_phone = models.CharField(max_length=20, blank=True)
    mother_full_name = models.CharField(max_length=150, blank=True)
    mother_phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name


class StudentAttendance(TimeStampedModel):
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'
    STATUS_LATE = 'late'
    STATUS_EXCUSED = 'excused'
    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Keldi'),
        (STATUS_ABSENT, 'Kelmadi'),
        (STATUS_LATE, 'Kech keldi'),
        (STATUS_EXCUSED, 'Sababli'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='attendance_records')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_attendance_records')
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date', 'student__first_name']

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"


class TeacherAttendance(TimeStampedModel):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_attendance_records')
    date = models.DateField(default=date.today)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    worked_minutes = models.PositiveIntegerField(default=0)
    is_late = models.BooleanField(default=False)
    left_early = models.BooleanField(default=False)
    check_in_latitude = models.DecimalField(max_digits=18, decimal_places=14, null=True, blank=True)
    check_in_longitude = models.DecimalField(max_digits=18, decimal_places=14, null=True, blank=True)
    check_out_latitude = models.DecimalField(max_digits=18, decimal_places=14, null=True, blank=True)
    check_out_longitude = models.DecimalField(max_digits=18, decimal_places=14, null=True, blank=True)

    class Meta:
        unique_together = ('teacher', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.teacher} - {self.date}"

    def calculate_worked_minutes(self):
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            self.worked_minutes = max(int(delta.total_seconds() // 60), 0)


def haversine_distance_meters(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    r = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


def validate_location_or_raise(latitude, longitude):
    settings_obj = SchoolSettings.get_solo()
    distance = haversine_distance_meters(latitude, longitude, settings_obj.latitude, settings_obj.longitude)
    is_allowed = distance <= settings_obj.allowed_radius_meters
    return is_allowed, round(distance, 2), settings_obj


def get_today_teacher_attendance(teacher):
    obj, _ = TeacherAttendance.objects.get_or_create(teacher=teacher, date=timezone.localdate())
    return obj
