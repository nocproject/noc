from django.db import models
from noc.main.report import report_registry

report_registry.register_all()
