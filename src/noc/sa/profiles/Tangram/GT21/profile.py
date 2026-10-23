#!/usr/bin/env python

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Tangram.GT21"

    pattern_more = [(rb"CTRL\+C.+?a All", b"\n")]
    pattern_prompt = rb"^>"
