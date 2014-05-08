# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Run Shell within IPython notebook
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import pkg_resources
## Django modules
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option


class Command(BaseCommand):
    help = "Run Notebook"

    def handle(self, *args, **options):
        from django.conf import settings
        from django.db.models.loading import get_models
        ## Check ipython is installed
        try:
            pkg_resources.require("ipython")
        except pkg_resources.DistributionNotFound:
            raise CommandError("ipython is not installed!\nPlease install ipython with:\n    ./bin/pip install ipython")
        ## Load models
        get_models()
        try:
            from IPython.html.notebookapp import NotebookApp
        except ImportError:
            from IPython.frontend.html.notebook import notebookapp
            NotebookApp = notebookapp.NotebookApp

        app = NotebookApp.instance()
        ipython_arguments = getattr(
            settings, "IPYTHON_ARGUMENTS",
            ["--ext", "django_extensions.management.notebook_extension"]
        )
        app.initialize(ipython_arguments)
        app.notebook_manager.notebook_dir = ".ipython"
        app.start()
