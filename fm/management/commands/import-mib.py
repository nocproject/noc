from django.core.management.base import BaseCommand
from django.db import transaction
from noc.fm.models import MIB

class Command(BaseCommand):
    help="Import MIB into database"
    def handle(self, *args, **options):
        transaction.enter_transaction_management()
        for a in args:
            MIB.load(a)
        transaction.commit()
        transaction.leave_transaction_management()

        