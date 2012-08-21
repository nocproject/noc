#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-stomp daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
import set_env

set_env.setup(use_django=False)

if __name__ == "__main__":
    from noc.main.stomp import STOMPDaemon
    STOMPDaemon().process_command()
