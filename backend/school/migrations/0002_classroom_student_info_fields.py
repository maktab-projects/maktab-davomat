# Manual migration for classroom/student information fields.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='last_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='student',
            name='gender',
            field=models.CharField(choices=[('male', 'Erkak'), ('female', 'Ayol')], max_length=10),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='subject',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='classroom',
            name='lesson_time',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='classroom',
            name='shift',
            field=models.CharField(choices=[('morning', 'Ertalab'), ('afternoon', 'Abetdan keyin')], default='morning', max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='father_full_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='student',
            name='father_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='mother_full_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='student',
            name='mother_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
