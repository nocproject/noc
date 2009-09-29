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
    name="Выписка из реестра Российской системы нумерации"
    description="Выписка из реестра Российской системы нумерации (коды ABC/DEF)"
    language="Russian"
    downloader="CSV"
    download_url="http://update.nocproject.org/db/russian_number_registry.csv.gz"
    refresh_interval=90
    fields=[
        Field(name="От (E.164)",search_method="starting"),
        Field(name="До (E.164)"),
        Field(name="АВС/DEF"),
        Field(name="Статус"),
        Field(name="От"),
        Field(name="До"),
        Field(name="Емкость"),
        Field(name="Оператор",search_method="starting"),
        Field(name="Регион")
        ]
