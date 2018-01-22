# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from common import schedule


class MainappConfig(AppConfig):
    name = 'mainapp'

    # FIXME: uncomment this
    # def ready(self):
    #     schedule.run_continuously()
