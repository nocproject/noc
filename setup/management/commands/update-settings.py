#!/usr/bin/env python
from django.core.management.base import BaseCommand
from noc.setup.models import register_defaults

class Command(BaseCommand):
    help="Generate rconfig config in a path specified py rconfig.path setting"
    def handle(self, *args, **options):
        register_defaults()
