# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from noc.peer.models import PeeringPoint

class Command(BaseCommand):
    help="Generate rconfig config in a path specified py rconfig.path setting"
    def handle(self, *args, **options):
        PeeringPoint.write_rconfig()
