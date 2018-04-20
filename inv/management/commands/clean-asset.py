# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc clean-asset
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection


class Command(BaseCommand):
    help = "Clean asset"

    def handle(self, *args, **options):
        clean = set()
        for expr in args:
            for obj in ManagedObjectSelector.resolve_expression(expr):
                if obj.id in clean:
                    continue  # Already cleaned
                self.clean_managed_object(obj)
                clean.add(obj.id)

    def clean_managed_object(self, object):
        for o in Object.objects.filter(
                data__management__managed_object=object.id):
            self.clean_obj(o)

    def clean_obj(self, obj):
        print "Cleaning %s %s (%s)" % (obj.model.name, obj.name, obj.id)
        # Clean children
        for o in Object.objects.filter(container=obj.id):
            self.clean_obj(o)
        # Clean inner connections
        for name, remote, remote_name in obj.iter_connections("i"):
            self.clean_obj(remote)
        obj.delete()