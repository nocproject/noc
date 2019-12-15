# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.ZyNOS.ES.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript


class Script(GetMetricsScript):
    """
    Tested on  ES-2024A. works only on firmware 3.90+
    via http://kb.zyxel.com/KB/searchArticle!gwsViewDetail.action?articleOid=012648&lang=EN
    """

    name = "Zyxel.ZyNOS.get_metrics"
