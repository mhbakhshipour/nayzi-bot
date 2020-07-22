from rest_framework import serializers
from django.utils.translation import ugettext as _
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from core.models import *


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'mobile', 'name', 'city', 'age', 'jalali_date_joined']


class ServiceImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSticker
        fields = ['image', 'description']


class ServiceListSerializer(serializers.ModelSerializer):
    images = ServiceImageListSerializer(many=True)

    class Meta:
        model = Service
        fields = ['title', 'images']


class UserServiceImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserServiceImage
        fields = ['image']


class UserServiceListSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    services = ServiceListSerializer()
    images = UserServiceImageListSerializer(many=True)

    class Meta:
        model = UserService
        fields = ['id', 'user', 'services', 'images', 'status', 'jalali_created_at']


class UserServiceDetailSerializer(serializers.ModelSerializer):
    user = UserListSerializer(required=False)
    services = ServiceListSerializer(required=False)
    images = UserServiceImageListSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        if 'user' in validated_data:
            user_status = validated_data.pop('status')
            instance.user.status = user_status.get('status', instance.user.status)
        super().update(instance, validated_data)
        return instance

    class Meta:
        model = UserService
        read_only_fields = ['user', 'services', 'images']
        fields = ['id', 'user', 'services', 'images', 'status', 'jalali_created_at']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    @staticmethod
    def validate_identifier(value):
        user = User.objects.get(username=value)
        if user.is_staff is True:
            return True
        raise serializers.ValidationError(_('Invalid username '))

    @staticmethod
    def __validate_password(password, username):
        try:
            user = User.objects.get(username=username)
            if user.is_staff is False:
                raise serializers.ValidationError(_('You not permitted to login in user area'))
            if not user.check_password(password):
                raise serializers.ValidationError(_('Invalid Password'))
        except User.DoesNotExist:
            raise serializers.ValidationError(_('Invalid username'))

    def validate(self, data):
        self.__validate_password(data['password'], data['username'])
        return data

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])
        data = {'status': 'ok', 'data': {'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)}}}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()

            data['refresh'] = str(refresh)

        return data