#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-classifier daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    from noc.fm.classifier import Classifier
    Classifier().process_command()
