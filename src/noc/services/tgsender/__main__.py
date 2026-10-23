# ----------------------------------------------------------------------
# tgsender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.tgsender.service import TgSenderService


if __name__ == "__main__":
    TgSenderService().start()
