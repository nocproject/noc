# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc get-uuod command
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import uuid
## NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("%s\n" % uuid.uuid4())

if __name__ == "__main__":
    Command().run()
