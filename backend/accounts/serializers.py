from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'subject', 'is_active', 'email'
        ]


class TeacherCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, required=False, allow_blank=True)
    parol = serializers.CharField(write_only=True, min_length=4, required=False, allow_blank=True)
    login = serializers.CharField(write_only=True, required=False, allow_blank=True)
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    full_name_input = serializers.CharField(write_only=True, required=False, allow_blank=True)
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'login', 'password', 'parol',
            'first_name', 'last_name', 'full_name', 'full_name_input', 'name',
            'phone', 'subject', 'email', 'role', 'is_active'
        ]
        extra_kwargs = {
            'username': {'required': False, 'allow_blank': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'role': {'required': False, 'read_only': True},
            'is_active': {'required': False},
        }

    def validate(self, attrs):
        login = (attrs.pop('login', '') or attrs.get('username', '')).strip()
        password = (attrs.pop('parol', '') or attrs.get('password', '')).strip()
        full_name = (
            attrs.pop('full_name_input', '')
            or attrs.pop('full_name', '')
            or attrs.pop('name', '')
        ).strip()

        if not login:
            raise serializers.ValidationError({'login': 'Login kiritilishi kerak'})
        if User.objects.filter(username=login).exists():
            raise serializers.ValidationError({'login': 'Bu login oldin ishlatilgan'})
        if not password:
            raise serializers.ValidationError({'password': 'Parol kiritilishi kerak'})

        first_name = (attrs.get('first_name') or '').strip()
        last_name = (attrs.get('last_name') or '').strip()
        if full_name and not first_name:
            parts = full_name.split()
            attrs['first_name'] = parts[0]
            attrs['last_name'] = ' '.join(parts[1:]) if len(parts) > 1 else last_name

        attrs['username'] = login
        attrs['password'] = password
        attrs['role'] = User.TEACHER
        attrs['is_staff'] = False
        attrs.setdefault('is_active', True)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        return UserSerializer(instance).data


class TeacherUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, required=False, allow_blank=True)
    parol = serializers.CharField(write_only=True, min_length=4, required=False, allow_blank=True)
    login = serializers.CharField(write_only=True, required=False, allow_blank=True)
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    full_name_input = serializers.CharField(write_only=True, required=False, allow_blank=True)
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'login', 'password', 'parol',
            'first_name', 'last_name', 'full_name', 'full_name_input', 'name',
            'phone', 'subject', 'email', 'is_active'
        ]
        extra_kwargs = {
            'username': {'required': False, 'allow_blank': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'is_active': {'required': False},
        }

    def validate(self, attrs):
        login = (attrs.pop('login', '') or attrs.get('username', '')).strip()
        if login:
            exists = User.objects.filter(username=login).exclude(pk=self.instance.pk).exists()
            if exists:
                raise serializers.ValidationError({'login': 'Bu login oldin ishlatilgan'})
            attrs['username'] = login

        password = (attrs.pop('parol', '') or attrs.get('password', '')).strip()
        if password:
            attrs['password'] = password
        else:
            attrs.pop('password', None)

        full_name = (
            attrs.pop('full_name_input', '')
            or attrs.pop('full_name', '')
            or attrs.pop('name', '')
        ).strip()
        if full_name:
            parts = full_name.split()
            attrs['first_name'] = parts[0]
            attrs['last_name'] = ' '.join(parts[1:]) if len(parts) > 1 else ''

        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.role = User.TEACHER
        instance.save()
        return instance

    def to_representation(self, instance):
        return UserSerializer(instance).data
