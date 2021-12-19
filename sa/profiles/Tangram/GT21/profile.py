#!/usr/bin/env python
__author__ = "boris"
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Tangram.GT21"

    pattern_more = rb"CTRL\+C.+?a All"
    pattern_prompt = rb"^>"
