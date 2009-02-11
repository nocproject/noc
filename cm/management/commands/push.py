# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
from noc.cm.models import Object


class Command(BaseCommand):
    help="Push objects"
    def handle(self, *args, **options):
        Object.global_push(args[0])
