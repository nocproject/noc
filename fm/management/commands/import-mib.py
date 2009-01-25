from django.core.management.base import BaseCommand
from noc.fm.models import MIB,MIBData

class Command(BaseCommand):
    help="Import MIB into database"
    def handle(self, *args, **options):
        for a in args:
            MIB.load(a)
        