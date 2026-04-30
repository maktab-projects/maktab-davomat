from django.core.management.base import BaseCommand

from accounts.models import User
from school.models import Classroom, SchoolSettings, Student, StudentAttendance, TeacherAttendance


class Command(BaseCommand):
    help = 'Create only director and admin. Teachers are created later from admin panel/API.'

    def handle(self, *args, **options):
        # User asked: ready teachers must be removed. Keep only director and admin.
        StudentAttendance.objects.all().delete()
        TeacherAttendance.objects.all().delete()
        Student.objects.all().delete()
        Classroom.objects.all().delete()
        User.objects.filter(role=User.TEACHER).delete()

        director, _ = User.objects.get_or_create(
            username='director',
            defaults={
                'first_name': 'Maktab',
                'last_name': 'Direktori',
                'role': User.DIRECTOR,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        director.role = User.DIRECTOR
        director.is_staff = True
        director.is_superuser = True
        director.set_password('director123')
        director.save()

        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Asosiy',
                'last_name': 'Admin',
                'role': User.ADMIN,
                'is_staff': True,
            }
        )
        admin.role = User.ADMIN
        admin.is_staff = True
        admin.set_password('admin123')
        admin.save()

        settings_obj = SchoolSettings.get_solo()
        settings_obj.school_name = 'Maktab CRM'
        settings_obj.save()

        self.stdout.write(self.style.SUCCESS(
            'Tayyor: director/director123 va admin/admin123 yaratildi. Tayyor ustozlar o‘chirildi; ustozlarni admin o‘zi yaratadi.'
        ))
