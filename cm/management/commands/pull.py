##
##
from django.core.management.base import BaseCommand
from noc.cm.models import Object


class Command(BaseCommand):
    help="Pull objects"
    def handle(self, *args, **options):
        Object.global_pull(args[0])