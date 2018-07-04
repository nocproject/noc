# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseDatasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class BaseReportDataSource(object):
    name = None  # Название
    columns = None  # Список колонок
    builtin_sorted = False  # поддержка сортировки
    unknown_value = None  # Fill empty value
    label = "?"

    def __init__(self, ids):
        self.ids = ids  # List of id for limit query
        self.out = None  # Save all loading

    def clean(self):
        pass

    def iter_data(self):
        for r in []:
            yield r

    def extract(self):
        """
        Generate list of rows. Each row is a list of fields. First value - is id
        :return:
        """
        raise NotImplementedError

    def load(self, ids, attributes):
        for ii in self.extract():
            self.out.update()
        return {i: [] for i in ids}

    def __getitem__(self, item):
        if not self.out:
            self.load(self.ids, [])
        # Old implementation
        return self.out.get(item, self.unknown_value)
