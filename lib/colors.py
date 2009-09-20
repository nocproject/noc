# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Color scheme generator
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

COLORS=[
    "#0000FF",
    "#7D00FF",
    "#FF00FF",
    "#FF007D",
    "#FF0000",
    "#FF7D00",
    "#FFFF00",
    "#7DFF00",
    "#00FF00",
    "#00FF7D",
    "#00FFFF",
    "#007DFF",
]
##
## Generate N contrast colors
##
def get_colors(N):
    for c in COLORS[:N]:
        yield c
