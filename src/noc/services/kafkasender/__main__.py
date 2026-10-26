# ----------------------------------------------------------------------
# kafkasender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.kafkasender.service import KafkaSenderService

if __name__ == "__main__":
    KafkaSenderService().start()
