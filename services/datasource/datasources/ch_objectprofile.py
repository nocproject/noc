# ----------------------------------------------------------------------
# CHNetworkSegment datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseDataSource
from noc.sa.models.managedobjectprofile import ManagedObjectProfile


class CHManagedObjectProfileDataSource(BaseDataSource):
    name = "ch_objectprofile"

    def extract(self):

        for mop in ManagedObjectProfile.objects.filter().iterator():
            yield (
                mop.bi_id,
                mop.id,
                mop.name,
                mop.level,
                int(mop.enable_ping),
                int(mop.enable_box_discovery),
                int(mop.enable_periodic_discovery),
            )
