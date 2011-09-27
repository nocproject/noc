# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Syncronize permissions
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.app import site
from noc.main.models import Permission


class Command(BaseCommand):
    """
    ./noc sync-perm
    """
    help = "Synchronize permissions"

    def handle(self, *args, **options):
        def normalize(app, perm):
            if ":" in perm:
                return perm
            return "%s:%s" % (app.get_app_id().replace(".", ":"), perm)

        def get_implied(name):
            try:
                return ",".join(implied_permissions[name])
            except KeyError:
                return None

        if not site.apps:
            site.autodiscover()  # Initialize applications to get permissions
        new_perms = set()
        implied_permissions = {}
        for app in site.apps.values():
            new_perms = new_perms.union(app.get_permissions())
            for p in app.implied_permissions:
                ips = sorted([normalize(app, pp)
                              for pp in app.implied_permissions[p]])
                implied_permissions[normalize(app, p)] = ips
        # Check all implied permissions are present
        for p in implied_permissions:
            if p not in new_perms:
                raise CommandError("Implied permission '%s' is not found" % p)
            nf = [pp for pp in implied_permissions[p] if pp not in new_perms]
            if nf:
                raise CommandError("Invalid implied permissions: %s" % ", ".join(pp))
        #
        old_perms = set(Permission.objects.values_list("name", flat=True))
        # New permissions
        for name in new_perms - old_perms:
            # @todo: add implied permissions
            Permission(name=name, implied=get_implied(name)).save()
            print "+ %s" % name
        # Check impiled permissions match
        for name in old_perms.intersection(new_perms):
            implied = get_implied(name)
            p = Permission.objects.get(name=name)
            if p.implied != implied:
                print "~ %s" % name
                p.implied = implied
                p.save()
        # Deleted permissions
        for name in old_perms - new_perms:
            print "- %s" % name
            Permission.objects.get(name=name).delete()
        # Check all users have implied permissions
        for p in Permission.objects.filter(implied__isnull=False):
            users = list(p.users.all())
            for ip in p.get_implied_permissions():
                for u in users:
                    if not ip.users.filter(id=u.id).exists():
                        ip.users.add(u)
