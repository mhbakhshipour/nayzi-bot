from django.db import models
from django.utils.translation import ugettext as _


class Service(models.Model):
    title = models.CharField(_('title'), max_length=255, unique=True, blank=False, null=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'services'
        verbose_name = _('service')
        verbose_name_plural = _('services')
