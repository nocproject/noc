# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Fix inventory tree
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel
import logging


def fix():
    # check "Lost&Found" container
    logging.info("Checking Lost&Found object")
    lostfound_model = ObjectModel.objects.get(uuid="b0fae773-b214-4edf-be35-3468b53b03f2")
    lf = Object.objects.filter(model=lostfound_model.id).count()
    if lf == 0:
        # Create missed "Lost&Found"
        logging.info("    ... creating missed Lost&Found")
        Object(model=lostfound_model.id, name="Global Lost&Found", container=None).save()
    elif lf == 1:
        logging.info("Global Lost&Found object found")  # OK
        # check container
        if Object.objects.get(name="Global Lost&Found").container:
            logging.info("Global Lost&Found object not valid container - fix")  # fix
            o = Object.objects.get(name="Global Lost&Found")
            o.container = None
            o.save()
        else:
            logging.info("Global Lost&Found object container is valid")
    else:
        logging.info("Global Lost&Found object found greater that one!!!!")
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

        if Object.objects.get(name="Global Lost&Found").container:
            logging.info("Global Lost&Found object not valid container - fix")  # fix
            o = Object.objects.get(name="Global Lost&Found")
            o.container = None
            o.save()
        else:
            logging.info("Global Lost&Found object container is valid")
