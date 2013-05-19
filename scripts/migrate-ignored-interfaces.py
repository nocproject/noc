#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Apply ignored_interfaces to given interface profile
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.models import Interface, InterfaceProfile
from noc.sa.models import ManagedObjectAttribute


def migrate(profile):
    print "Setting profile %s" % profile.name
    for a in ManagedObjectAttribute.objects.filter(key="ignored_interfaces"):
        mo = a.managed_object
        ignored = []
        for iface in Interface.objects.filter(managed_object=mo.id):
            if mo.is_ignored_interface(iface.name):
                iface.profile = profile
                iface.save()
                ignored += [iface.name]
        if ignored:
            print "%s: %s" % (
                mo.name, ", ".join(ignored)
            )
            a.delete()

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print "Usage"
        print "%s <interface profile name>" % sys.argv[0]
        sys.exit(1)

    profile = InterfaceProfile.objects.filter(name=sys.argv[1]).first()
    if not profile:
        print "Invalid interface profile. Existing profiles are:"
        for profile in InterfaceProfile.objects.all():
            print profile

    migrate(profile)
