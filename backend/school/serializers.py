from django.utils import timezone
from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import (
    Classroom, SchoolSettings, Student, StudentAttendance, TeacherAttendance,
)


class SchoolSettingsSerializer(serializers.ModelSerializer):
    location_label = serializers.SerializerMethodField()

    class Meta:
        model = SchoolSettings
        fields = '__all__'

    def get_location_label(self, obj):
        return 'Lokatsiya sozlamasi yopiq'


class ClassroomSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True)
    subject = serializers.CharField(required=False, allow_blank=True)
    teacher_detail = UserSerializer(source='teacher', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    shift_display = serializers.CharField(source='get_shift_display', read_only=True)

    class Meta:
        model = Classroom
        fields = [
            'id', 'teacher', 'teacher_detail', 'teacher_name', 'name', 'grade_level', 'subject',
            'room', 'lesson_time', 'shift', 'shift_display', 'schedule_info',
            'is_active', 'student_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['teacher']

    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() or obj.teacher.username

    def get_student_count(self, obj):
        return obj.students.filter(is_active=True).count()

    def validate(self, attrs):
        lesson_time = attrs.get('lesson_time') or getattr(self.instance, 'lesson_time', '')
        shift = attrs.get('shift') or getattr(self.instance, 'shift', Classroom.SHIFT_MORNING)
        room = attrs.get('room') or getattr(self.instance, 'room', '')
        shift_label = dict(Classroom.SHIFT_CHOICES).get(shift, shift)
        if not attrs.get('name') and not getattr(self.instance, 'name', ''):
            parts = [part for part in [room, lesson_time, shift_label] if part]
            attrs['name'] = ' - '.join(parts) or f"Sinf {timezone.now().strftime('%Y%m%d%H%M%S')}"
        attrs['subject'] = attrs.get('subject', '') or ''
        if lesson_time and not attrs.get('schedule_info'):
            attrs['schedule_info'] = f"{shift_label} | {lesson_time}"
        return attrs


class StudentSerializer(serializers.ModelSerializer):
    # first_name backendda majburiy bo'lsa ham serializerda optional: ism-familya bitta inputdan ajratiladi.
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)
    full_name_input = serializers.CharField(write_only=True, required=False, allow_blank=True)
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    ism_familyasi = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone_number = serializers.CharField(source='phone_primary', required=False, allow_blank=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'classroom', 'classroom_name', 'teacher_name',
            'first_name', 'last_name', 'middle_name', 'full_name', 'full_name_input',
            'name', 'ism_familyasi',
            'birth_date', 'gender', 'gender_display', 'phone_primary', 'phone_number',
            'phone_secondary', 'parent_name', 'father_full_name', 'father_phone',
            'mother_full_name', 'mother_phone', 'address', 'is_active',
            'created_at', 'updated_at'
        ]

    def get_teacher_name(self, obj):
        teacher = obj.classroom.teacher
        return teacher.get_full_name() or teacher.username

    def validate(self, attrs):
        full_name_input = (
            attrs.pop('full_name_input', '')
            or attrs.pop('name', '')
            or attrs.pop('ism_familyasi', '')
            or ''
        ).strip()
        first_name = (attrs.get('first_name') or getattr(self.instance, 'first_name', '') or '').strip()
        if full_name_input and not first_name:
            parts = full_name_input.split()
            attrs['first_name'] = parts[0]
            attrs['last_name'] = ' '.join(parts[1:]) if len(parts) > 1 else ''
        elif 'first_name' in attrs:
            attrs['first_name'] = attrs.get('first_name', '').strip()
        if not attrs.get('first_name') and not getattr(self.instance, 'first_name', ''):
            raise serializers.ValidationError({'full_name_input': 'Ism familyasi kiritilishi kerak'})
        return attrs


class StudentAttendanceSerializer(serializers.ModelSerializer):
    student_detail = StudentSerializer(source='student', read_only=True)

    class Meta:
        model = StudentAttendance
        fields = [
            'id', 'student', 'student_detail', 'classroom', 'teacher', 'date',
            'status', 'note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['teacher']


class BulkAttendanceItemSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=StudentAttendance.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True)


class BulkAttendanceSerializer(serializers.Serializer):
    classroom_id = serializers.IntegerField()
    date = serializers.DateField(default=timezone.localdate)
    records = BulkAttendanceItemSerializer(many=True)


class TeacherAttendanceSerializer(serializers.ModelSerializer):
    teacher_detail = UserSerializer(source='teacher', read_only=True)
    worked_hours = serializers.SerializerMethodField()

    class Meta:
        model = TeacherAttendance
        fields = [
            'id', 'teacher', 'teacher_detail', 'date', 'check_in_time', 'check_out_time',
            'worked_minutes', 'worked_hours', 'is_late', 'left_early',
            'check_in_latitude', 'check_in_longitude', 'check_out_latitude', 'check_out_longitude'
        ]

    def get_worked_hours(self, obj):
        hours = obj.worked_minutes // 60
        minutes = obj.worked_minutes % 60
        return f"{hours} soat {minutes} daqiqa"



class CheckInOutSerializer(serializers.Serializer):
    # Frontend navigator.geolocation orqali yuborgan haqiqiy koordinatalar majburiy.
    # Oldin latitude/longitude kelmasa, maktabning o'z koordinatasi avtomatik qo'yilgan edi;
    # shu sababli keldim/ketdim tugmasi hamma joyda ishlayvergan.
    latitude = serializers.DecimalField(max_digits=18, decimal_places=14, required=False)
    longitude = serializers.DecimalField(max_digits=18, decimal_places=14, required=False)
    lat = serializers.DecimalField(max_digits=18, decimal_places=14, required=False)
    lng = serializers.DecimalField(max_digits=18, decimal_places=14, required=False)

    def validate(self, attrs):
        latitude = attrs.get('latitude', attrs.get('lat'))
        longitude = attrs.get('longitude', attrs.get('lng'))

        if latitude is None or longitude is None:
            raise serializers.ValidationError({
                'detail': 'Lokatsiya olinmadi. Telefon/browserdan lokatsiyaga ruxsat berib, qayta urinib ko‘ring.'
            })

        latitude_float = float(latitude)
        longitude_float = float(longitude)

        if not (-90 <= latitude_float <= 90):
            raise serializers.ValidationError({'latitude': 'Latitude noto‘g‘ri qiymat.'})
        if not (-180 <= longitude_float <= 180):
            raise serializers.ValidationError({'longitude': 'Longitude noto‘g‘ri qiymat.'})

        attrs['latitude'] = latitude
        attrs['longitude'] = longitude
        attrs.pop('lat', None)
        attrs.pop('lng', None)
        return attrs
