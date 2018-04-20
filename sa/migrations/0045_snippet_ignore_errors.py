# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Add CommandSnippet.ignore_cli_errors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db
# NOC modules
=======
##----------------------------------------------------------------------
## Add CommandSnippet.ignore_cli_errors
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from django.db import models


class Migration:
    def forwards(self):
        db.add_column("sa_commandsnippet", "ignore_cli_errors",
                      models.BooleanField("Ignore CLI errors", default=False))

    def backwards(self):
        db.delete_column("sa_commandsnippet", "ignore_cli_errors")
