# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.fm.models import *

COLORS={
    "CRITICAL":("#BB0000","#FFDDCC"),
    "MAJOR"   :("#BB0000","#FFEEDD"),
    "MINOR"   :("#BB0000","#FFFFBB"),
    "WARNING" :("#BB0000","#FFFFDD"),
    "NORMAL"  :("#BB0000","#A8C2C2"),
    "INFO"    :("#BB0000","#DCF3F3"),
    "DEFAULT" :("#FFFF00","#643200"),
}

class Migration:
    
    def forwards(self):
        for p,colors in COLORS.items():
            font,bg=colors
            r=db.execute("SELECT id,font_color,background_color FROM fm_eventpriority WHERE name=%s",[p])
            if len(r)==1:
                pid,dbf,dbg=r[0]
                if not dbf:
                    db.execute("UPDATE fm_eventpriority SET font_color=%s WHERE id=%s",[font,pid])
                if not dbf:
                    db.execute("UPDATE fm_eventpriority SET background_color=%s WHERE id=%s",[bg,pid])
                
    
    def backwards(self):
        "Write your backwards migration here"
