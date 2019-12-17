# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Deprecation Warning classes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
On every new NOC release ensure:

* All features with RemovedInNOC<current>Warning is really removed from code
* Remove unnecessary deprecation warning
* Mark Next Release's warnings as DeprecationWarning
* Add Next-after-next Release's warnings as PendingDeperecationWarning
"""


class RemovedInNOC2001Warning(DeprecationWarning):
    """
    Features to be removed in NOC 20.1
    """


class RemovedInNOC2002Warning(PendingDeprecationWarning):
    """
    Features to be removed in NOC 20.2
    """
