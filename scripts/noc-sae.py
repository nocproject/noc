#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-sae daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    # Run SAE
    from noc.sa.sae import SAE
    SAE().process_command()
