# ----------------------------------------------------------------------
#  Timezone setting
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import time

# NOC modules
from noc.config import config

ZONEINFO_ROOT = "/usr/share/zoneinfo"


def setup_timezone():
    """
    Set timezone from config.timezone
    :return:
    """
    if not hasattr(time, "tzset") or not config.timezone:
        return  # Not supported anyway
    if not has_timezone(str(config.timezone)):
        raise ValueError("Invalid timezone: %s" % config.timezone)
    os.environ["TZ"] = str(config.timezone)
    time.tzset()


def has_timezone(tzname):
    path = os.path.join(*([ZONEINFO_ROOT, *tzname.split("/")]))
    return os.path.exists(path)
