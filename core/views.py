from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import ugettext as _
from rest_framework_simplejwt.views import TokenViewBase

from bot.custom_view_mixins import ExpressiveListModelMixin, ExpressiveUpdateModelMixin
from bot.exceptions import HttpUnauthorizedException
from core.models import UserService, User
from core.serializers import UserServiceListSerializer, UserServiceDetailSerializer, LoginSerializer, \
    TokenRefreshSerializer


class UserServiceView(ExpressiveListModelMixin, generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserServiceListSerializer
    plural_name = 'user_list'

    def get_queryset(self):
        queryset = UserService.objects.all().order_by('-created_at')
        return queryset


class UserDetailView(ExpressiveUpdateModelMixin, generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    singular_name = 'user'
    serializer_class = UserServiceDetailSerializer

    def get_object(self):
        return UserService.objects.get(pk=self.kwargs['user_id'])


class LoginView(APIView):
    def get_serializer(self):
        """ Used for swagger input inspection"""
        return LoginSerializer()

    @staticmethod
    def _authenticate(request):
        credentials = request.data
        try:
            user = User.objects.get(username=credentials['username'])
        except User.DoesNotExist:
            raise HttpUnauthorizedException(_('User does not exists'))
        if user.is_staff is False:
            raise HttpUnauthorizedException(_('You not permitted to login in user area'))
        return user

    @staticmethod
    def _generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}

    def post(self, request):
        login_serializer = LoginSerializer(data=request.data)
        login_serializer.is_valid(raise_exception=True)
        user = self._authenticate(request)

        tokens = self._generate_tokens(user)
        return Response({'status': 'ok', 'data': {'tokens': tokens}})


class TokenRefreshView(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """
    serializer_class = TokenRefreshSerializer
