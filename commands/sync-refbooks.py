# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Load and syncronize built-in refbooks
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import os

# Third-party modules
import six

# NOC modules
from noc.core.management.base import BaseCommand
from noc.main.refbooks.refbooks import RefBook
from noc.main.models.refbook import RefBook as RB
from noc.core.comp import smart_text


class Command(BaseCommand):
    help = "Synchronize built-in Reference Books"

    def handle(self, *args, **options):
        self.sync_refbooks()

    #
    # Search for subclasses of givent class inside given directory
    #
    def search(self, cls, d):
        classes = {}
        for dirpath, dirnames, filenames in os.walk(d):
            mb = "noc.main." + ".".join(dirpath.split(os.sep)[1:]) + "."
            for f in [
                f
                for f in filenames
                if f.endswith(".py") and f != "__init__.py" and not f.startswith(".")
            ]:
                m = __import__(mb + f[:-3], {}, {}, "*")
                for ec_name in dir(m):
                    ec = getattr(m, ec_name)
                    try:
                        if not issubclass(ec, cls) or ec == cls:
                            continue
                    except Exception:
                        continue
                    classes[ec] = None
        return list(classes)

    def sync_refbooks(self):
        # Make built-in refbooks inventory
        loaded_refbooks = {}
        for rb in RB.objects.filter(is_builtin=True):
            loaded_refbooks[rb.name] = rb
        for r in self.search(RefBook, "main/refbooks/refbooks"):
            name = smart_text(r.name, "utf-8")
            r.sync()
            if name in loaded_refbooks:
                del loaded_refbooks[name]
        # Delete stale refbooks
        for rb in six.itervalues(loaded_refbooks):
            self.print("DELETE REFBOOK: %s" % rb.name)
            rb.delete()


if __name__ == "__main__":
    Command().run()
