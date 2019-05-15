# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DataSource model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
# NOC modules
import noc.lib.nosql as nosql


@six.python_2_unicode_compatible
class DataSource(nosql.EmbeddedDocument):
    meta = {
        "strict": False,
        "auto_create_index": False
    }
    name = nosql.StringField()
    datasource = nosql.StringField()
    search = nosql.DictField()

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.datasource == other.datasource and
            self.search == other.search
        )
