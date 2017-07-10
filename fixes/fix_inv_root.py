# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Fix inventory tree
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
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
        logging.info("Root object found")  # OK
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

    # chech "Lost&Found" container
    logging.info("Checking Loste&Found object")
    lostfound_model = ObjectModel.objects.get(uuid="b0fae773-b214-4edf-be35-3468b53b03f2")
    lf = Object.objects.filter(model=lostfound_model.id).count()
    if lf == 0:
        # Create missed "Lost&Found"
        logging.info("    ... creating missed Lost&Found")
        Object(model=lostfound_model.id, name="Global Lost&Found", container=Object(name="Root").id).save()
    elif lf == 1:
        logging.info("Global Lost&Found object found")  # OK
        # check container
        #print Object.objects.filter(name="Global Lost&Found") , "Root: ", Object.objects.filter(name="Root")
        #print Object.objects.get(name="Global Lost&Found").container , Object.objects.get(name="Root").id

        if Object.objects.get(name="Global Lost&Found").container != Object.objects.get(name="Root",model=root_model).id:
            logging.info("Global Lost&Found object not valid container - fix")  # fix
            o = Object.objects.get(name="Global Lost&Found")
            o.container = Object.objects.get(name="Root").id
            o.save()
        else:
            logging.info("Global Lost&Found object container is valid")

    else:
        logging.info("Global Lost&Found object found great that one!!!!")
        # merge Lost&found
        lfs = Object.objects.filter(model=lostfound_model.id).order_by("id")
        l0 = lfs[0]
        for l in lfs[1:]:
            for ls in Object.objects.filter(container=l.id):
                logging.info("    ... moving %s to primary Lost&Found", unicode(ls))
                ls.container = l0.id
                ls.save()
            logging.info("   ... removing duplicated Lost&Found %s", l)
            l.delete()

        if Object.objects.get(name="Global Lost&Found").container != Object.objects.get(name="Root",model=root_model).id:
            logging.info("Global Lost&Found object not valid container - fix")  # fix
            o = Object.objects.get(name="Global Lost&Found")
            o.container = Object.objects.get(name="Root").id
            o.save()
        else:
            logging.info("Global Lost&Found object container is valid")







