from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from .permissions import IsDirectorOrAdmin
from .serializers import TeacherCreateSerializer, TeacherUpdateSerializer, UserSerializer


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class TeacherListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsDirectorOrAdmin]

    def create(self, request, *args, **kwargs):
        if request.user.role != User.ADMIN:
            raise PermissionDenied('Ustozni faqat admin yaratadi')
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = User.objects.filter(role=User.TEACHER).order_by('first_name', 'last_name', 'username')
        include_inactive = self.request.query_params.get('include_inactive') in ['1', 'true', 'True']
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TeacherCreateSerializer
        return UserSerializer


class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsDirectorOrAdmin]
    queryset = User.objects.filter(role=User.TEACHER)

    def update(self, request, *args, **kwargs):
        if request.user.role != User.ADMIN:
            raise PermissionDenied('Ustozni faqat admin o‘zgartiradi')
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if request.user.role != User.ADMIN:
            raise PermissionDenied('Ustozni faqat admin o‘zgartiradi')
        return super().partial_update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TeacherUpdateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        if request.user.role != User.ADMIN:
            raise PermissionDenied('Ustozni faqat admin o‘chiradi')
        teacher = self.get_object()
        teacher.is_active = False
        teacher.save(update_fields=['is_active'])
        return Response({'detail': 'Ustoz o‘chirildi'}, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsDirectorOrAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('role', 'first_name', 'last_name', 'username')


class RoleSummaryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsDirectorOrAdmin]

    def get(self, request, *args, **kwargs):
        data = {
            'directors': User.objects.filter(role=User.DIRECTOR, is_active=True).count(),
            'admins': User.objects.filter(role=User.ADMIN, is_active=True).count(),
            'teachers': User.objects.filter(role=User.TEACHER, is_active=True).count(),
        }
        return Response(data)
