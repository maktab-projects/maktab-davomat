from django.urls import path
from .views import MeView, RoleSummaryView, TeacherDetailView, TeacherListCreateView, UserListView

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
    path('teachers/', TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('teachers/<int:pk>/', TeacherDetailView.as_view(), name='teacher-detail'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('role-summary/', RoleSummaryView.as_view(), name='role-summary'),
]
