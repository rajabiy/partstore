from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext as _


class StoreConfig(AppConfig):
    name = 'store'


    def ready(self):
        self.app_label = _('store sales')
        self.verbose_name = _('store sales')
        from store.signals import *
