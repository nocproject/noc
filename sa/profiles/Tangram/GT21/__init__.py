<<<<<<< HEAD
#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'boris'
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Tangram.GT21"
    pattern_more = "CTRL\+C.+?a All"
    pattern_prompt = r"^>"
=======
# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'boris'
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, HTTP


class Profile(noc.sa.profiles.Profile):
    name = "Tangram.GT21"
    supported_schemes = [TELNET, HTTP]
    pattern_more = "CTRL\+C.+?a All"
    pattern_prompt = r"^>"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
