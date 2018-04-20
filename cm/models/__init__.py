# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Configuration Management models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Configuration Management models
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import datetime
import logging
import types
import difflib
## Django modules
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
## NOC modules
from noc.sa.profiles import profile_registry
from noc.settings import config
from noc.lib.fileutils import rewrite_when_differ, read_file, is_differ, in_dir
from noc.lib.validators import is_int
from noc.cm.vcs import vcs_registry
from noc.sa.models import AdministrativeDomain, ManagedObject
from noc.main.models import NotificationGroup
from noc.lib.app.site import site


profile_registry.register_all()
vcs_registry.register_all()

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from objectnotify import ObjectNotify, OBJECT_TYPE_CHOICES, OBJECT_TYPES
from object import Object
from prefixlist import PrefixList
from rpsl import RPSL

from errortype import ErrorType
