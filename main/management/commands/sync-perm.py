# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Syncronize permissions
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
from noc.lib.app import site
from noc.main.models import Permission
##
## Command handler
##
class Command(BaseCommand):
    help="Syncronize permissions"
    def handle(self, *args, **options):
        new_perms=set()
        for app in site.apps.values():
            new_perms=new_perms.union(app.get_permissions())
        old_perms=set(Permission.objects.values_list("name",flat=True))
        # New permissions
        for name in new_perms-old_perms:
            Permission(name=name).save()
            print "+ %s"%name
        # Deleted permissions
        for name in old_perms-new_perms:
            print "- %s"%name
            Permission.objects.get(name=name).delete()
