from __future__ import unicode_literals

from django.apps import AppConfig


class StoreConfig(AppConfig):
    name = 'store'

    def ready(self):
        from store.signals import *
