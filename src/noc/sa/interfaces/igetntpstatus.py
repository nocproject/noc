# ---------------------------------------------------------------------
# IGetNTPStatus interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import DictListParameter, StringParameter, IntParameter, BooleanParameter, IPParameter


class IGetNTPStatus(BaseInterface):
    """

    * name - optional association name
    * address - address
    * stratum - NTP stratum
    * version - optional NTP protocol version
    * status - one of:
        * unknown - connection failed or sanity check not passed
        * sane - sanity check passed (RFC-1303)
        * selected - peer is selected for synchronization
        * master - peer is master
    * is_synchronized - true, if synchronized
    * ref_id - reference label (i.e. `GPS`). See RFC-5906 for valid clock sources.
    """

    returns = DictListParameter(
        attrs={
            "name": StringParameter(required=False),
            "address": IPParameter(),
            "stratum": IntParameter(),
            "version": IntParameter(required=False),
            "ref_id": StringParameter(required=False),
            "is_synchronized": BooleanParameter(),
            "status": StringParameter(choices=["unknown", "sane", "selected", "master"]),
        }
    )
