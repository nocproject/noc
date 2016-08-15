# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Convert legacy PoP links
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel
import logging


def fix():
    root_model = ObjectModel.objects.get(uuid="0f1b7c90-c611-4046-9a83-b120377eb6e0")
    logging.info("Checking inventory Root")
    rc = Object.objects.filter(model=root_model.id).count()
    if rc == 0:
        # Create missed root
        logging.info("    ... creating missed root")
        Object(model=root_model, name="Root").save()
    elif rc == 1:
        return  # OK
    else:
        # Merge roots
        roots = Object.objects.filter(model=root_model.id).order_by("id")
        r0 = roots[0]
        for r in roots[1:]:
            for o in Object.objects.filter(container=r.id):
                logging.info("    ... moving %s to primary root", unicode(o))
                o.container = r0.id
                o.save()
            logging.info("   ... removing duplicated root %s", r)
            r.delete()
