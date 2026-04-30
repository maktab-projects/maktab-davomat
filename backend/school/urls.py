from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceDayFilterView,
    AttendanceDayExportView,
    AttendanceListView,
    BulkAttendanceCreateView,
    ClassroomInfoExportView,
    ClassroomInfoView,
    ClassroomViewSet,
    DashboardOverviewView,
    DirectorMalumotlarExportView,
    DirectorMalumotlarView,
    MalumotlarExportView,
    MalumotlarView,
    SchoolSettingsView,
    StudentViewSet,
    TeacherCheckInView,
    TeacherCheckOutView,
    TeacherAttendanceReportExportView,
    TeacherAttendanceReportView,
    TodayTeacherAttendanceView,
)

router = DefaultRouter()
router.register('classrooms', ClassroomViewSet, basename='classrooms')
router.register('students', StudentViewSet, basename='students')

urlpatterns = [
    path('', include(router.urls)),
    path('school-settings/', SchoolSettingsView.as_view(), name='school-settings'),
    path('attendance/', AttendanceListView.as_view(), name='attendance-list'),
    path('attendance/day-filter/', AttendanceDayFilterView.as_view(), name='attendance-day-filter'),
    path('attendance/day-filter/export/', AttendanceDayExportView.as_view(), name='attendance-day-export'),
    path('attendance/bulk-save/', BulkAttendanceCreateView.as_view(), name='attendance-bulk-save'),
    path('teacher-attendance/check-in/', TeacherCheckInView.as_view(), name='teacher-check-in'),
    path('teacher-attendance/check-out/', TeacherCheckOutView.as_view(), name='teacher-check-out'),
    path('teacher-attendance/today/', TodayTeacherAttendanceView.as_view(), name='teacher-attendance-today'),
    path('teacher-attendance/report/', TeacherAttendanceReportView.as_view(), name='teacher-attendance-report'),
    path('teacher-attendance/report/export/', TeacherAttendanceReportExportView.as_view(), name='teacher-attendance-report-export'),
    path('classroom-info/', ClassroomInfoView.as_view(), name='classroom-info'),
    path('classroom-info/export/', ClassroomInfoExportView.as_view(), name='classroom-info-export'),
    path('malumotlar/', MalumotlarView.as_view(), name='malumotlar'),
    path('malumotlar/export/', MalumotlarExportView.as_view(), name='malumotlar-export'),
    path('director/malumotlar/', DirectorMalumotlarView.as_view(), name='director-malumotlar'),
    path('director/malumotlar/export/', DirectorMalumotlarExportView.as_view(), name='director-malumotlar-export'),
    path('dashboard/overview/', DashboardOverviewView.as_view(), name='dashboard-overview'),
]
