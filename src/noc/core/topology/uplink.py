# ----------------------------------------------------------------------
# Calculate topology uplinks
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.sa.models.managedobject import ManagedObject, ObjectUplinks
from noc.core.debug import ErrorReport
from noc.config import config

logger = logging.getLogger(__name__)


def update_uplinks(**kwargs):
    from noc.services.topo.topo import Topo
    from noc.services.topo.types import ObjectSnapshot

    topo = Topo(check=True)
    for mo_id, level, links, uplinks in ManagedObject.objects.filter().values_list(
        "id", "object_profile__level", "links", "uplinks"
    ):
        topo.sync_object(
            ObjectSnapshot(id=mo_id, level=level, links=links or None, uplinks=uplinks or None)
        )
    with ErrorReport():
        affected = topo.process()
        if affected and not config.topo.dry_run:
            # logger.info("Commiting uplink changes")
            # @todo: RCA neighbors
            up_links = []
            for obj_id in affected:
                try:
                    up_links.append(
                        ObjectUplinks(
                            object_id=obj_id,
                            uplinks=sorted(topo.get_uplinks(obj_id)),
                            rca_neighbors=sorted(topo.get_rca_neighbors(obj_id)),
                        )
                    )
                except KeyError:
                    logger.warning("Deleted object with id: %s", obj_id)
            ManagedObject.update_uplinks(up_links)
            logger.info("%d changes has been commited", len(affected))
