# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Russian Number Plan (E.164 +7 zone)
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.main.refbooks.refbooks import RefBook,Field

##
## Russian Number Plan
##
class RussianNumberPlan(RefBook):
    name="Российский План Нумерации"
    description="Российский план нумерации, коды ABC"
    language="Russian"
    downloader="CSV"
    download_url="http://update.nocproject.org/db/russian_number_plan.csv"
    refresh_interval=90
    fields=[
        Field(name="Зона нумерации",search_method="substring"),
        Field(name="Субъект Федерации",search_method="substring"),
        Field(name="Код ABC",search_method="substring"),
        ]
