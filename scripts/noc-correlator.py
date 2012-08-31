#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-correlator daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
import set_env

set_env.setup(use_django=True)

if __name__ == "__main__":
    from noc.fm.correlator.daemon import Correlator
    Correlator().process_command()
