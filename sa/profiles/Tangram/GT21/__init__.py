# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'boris'
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Tangram.GT21"
    pattern_more = "CTRL\+C.+?a All"
    pattern_prompt = r"^>"
