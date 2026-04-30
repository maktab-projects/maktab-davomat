# Generated to support high precision school location for attendance check-in/out.

from decimal import Decimal

from django.db import migrations, models


def set_fixed_school_location(apps, schema_editor):
    SchoolSettings = apps.get_model('school', 'SchoolSettings')
    SchoolSettings.objects.update_or_create(
        pk=1,
        defaults={
            'latitude': Decimal('41.08022969852711'),
            'longitude': Decimal('69.04543362274605'),
            'allowed_radius_meters': 120,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0002_classroom_student_info_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolsettings',
            name='latitude',
            field=models.DecimalField(decimal_places=14, default=Decimal('41.08022969852711'), max_digits=18),
        ),
        migrations.AlterField(
            model_name='schoolsettings',
            name='longitude',
            field=models.DecimalField(decimal_places=14, default=Decimal('69.04543362274605'), max_digits=18),
        ),
        migrations.AlterField(
            model_name='teacherattendance',
            name='check_in_latitude',
            field=models.DecimalField(blank=True, decimal_places=14, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='teacherattendance',
            name='check_in_longitude',
            field=models.DecimalField(blank=True, decimal_places=14, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='teacherattendance',
            name='check_out_latitude',
            field=models.DecimalField(blank=True, decimal_places=14, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='teacherattendance',
            name='check_out_longitude',
            field=models.DecimalField(blank=True, decimal_places=14, max_digits=18, null=True),
        ),
        migrations.RunPython(set_fixed_school_location, migrations.RunPython.noop),
    ]
