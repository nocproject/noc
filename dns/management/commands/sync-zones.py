# encoding: utf-8
from django.core.management.base import BaseCommand
from noc.dns.models import DNSZone

class Command(BaseCommand):
    help="Generate DNS Zones"
    def handle(self, *args, **options):
        DNSZone.sync_zones()