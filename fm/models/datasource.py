# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DataSource model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## DataSource model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import noc.lib.nosql as nosql


class DataSource(nosql.EmbeddedDocument):
    meta = {
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }
    name = nosql.StringField()
    datasource = nosql.StringField()
    search = nosql.DictField()

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.datasource == other.datasource and
            self.search == other.search
        )

