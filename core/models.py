import re

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Manager
from django.utils.translation import ugettext as _

from bot import settings


class UserManager(BaseUserManager):
    """Custom user manager suited for mobile authentication base"""
    use_in_migrations = True

    @staticmethod
    def is_mobile(value):
        rule = re.compile(r'^09[0-9]{9}$')
        if not rule.search(value):
            raise ValueError('Invalid mobile number')

    def __create_user(self, username, password, **extra_fields):
        """
        Creates and saves a User with the mobile
        """
        if not username:
            raise ValueError('A username number should be provided')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self.__create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.__create_user(username, password, **extra_fields)

    def get_telegram_users(self, count, offset):
        return self.filter(telegram_id__isnull=False, is_staff=False)[offset: count + offset]


class User(AbstractBaseUser, PermissionsMixin):
    telegram_id = models.CharField(_('telegram_id'), max_length=20, unique=True, blank=True, null=True)
    username = models.CharField(_('username'), max_length=255, unique=True, null=True, blank=True)
    mobile = models.CharField(_('mobile'), max_length=11, blank=True, null=True)
    name = models.CharField(_('name'), max_length=100, blank=True, null=True)
    city = models.CharField(_('city'), max_length=100, blank=True, null=True)
    age = models.SmallIntegerField(_('age'), blank=True, null=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username if self.username else self.telegram_id


class UserActivityManager(Manager):
    def get_user_activity(self, user):
        return self.filter(user=user)

    def log_story_selection(self, user, story):
        return self.create(user=user, action='choose', story=story)

    def log_user_started_the_bot(self, user):
        return self.create(user=user, action='start')

    def log_user_again_started_the_bot(self, user):
        return self.create(user=user, action='again_start')

    def log_conversation_viewed(self, user, conversation):
        return self.create(user=user, action='view', conversation=conversation)


class UserActivity(models.Model):
    action_choices = (
        ('start', _('start')),
        ('again_start', _('again_start')),
        ('get_contact_us', _('get_contact_us')),
        ('choice_service_uncompleted', _('choice_service_uncompleted')),
        ('choice_service_completed', _('choice_service_completed')),
        ('send_information', _('send_information')),
    )
    user = models.ForeignKey(to="User", on_delete=models.CASCADE, verbose_name=_('user'))
    action = models.CharField(_('action'), max_length=255, choices=action_choices)
    services = models.ManyToManyField(verbose_name='services', to="Service", related_name='user_services')
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('created_at'))

    objects = UserActivityManager()

    class Meta:
        db_table = 'user_activities'
        verbose_name = _('user_activity')
        verbose_name_plural = _('user_activities')

    def __str__(self):
        return 'فعالیت کاربر با شناسه' + ' ' + str(self.user.telegram_id)


class ServiceSticker(models.Model):
    image = models.ImageField(_('image'), upload_to=settings.UPLOAD_DIRECTORIES['service_sticker'])
    description = models.TextField(_('description'), blank=False, null=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    # def jalali_created_at(self):
    #     return datetime2jalali(self.created_at).strftime('%y/%m/%d')

    class Meta:
        db_table = 'service_stickers'
        verbose_name = _('service_sticker')
        verbose_name_plural = _('service_stickers')

    def __str__(self):
        return self.description


class Service(models.Model):
    title = models.CharField(_('title'), max_length=255, unique=True, blank=False, null=False)
    images = models.ManyToManyField(verbose_name=_('images'), to="ServiceSticker", related_name='service_sticker',
                                    blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'services'
        verbose_name = _('service')
        verbose_name_plural = _('services')
