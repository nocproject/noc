# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Refbook
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
# Third-party modules
from django.db import models
# NOC modules
from language import Language
from noc.main.refbooks.downloaders import downloader_registry

downloader_registry.register_all()


class RefBook(models.Model):
    """
    Reference Books
    """

    class Meta:
        verbose_name = "Ref Book"
        verbose_name_plural = "Ref Books"

    name = models.CharField("Name", max_length=128, unique=True)
    language = models.ForeignKey(Language,
                                 verbose_name="Language")
    description = models.TextField("Description", blank=True, null=True)
    is_enabled = models.BooleanField("Is Enabled", default=False)
    is_builtin = models.BooleanField("Is Builtin", default=False)
    downloader = models.CharField(
        "Downloader", max_length=64,
        choices=downloader_registry.choices,
        blank=True, null=True)
    download_url = models.CharField(
        "Download URL",
        max_length=256, null=True,
        blank=True)
    last_updated = models.DateTimeField(
        "Last Updated", blank=True,
        null=True)
    next_update = models.DateTimeField(
        "Next Update", blank=True,
        null=True)
    refresh_interval = models.IntegerField(
        "Refresh Interval (days)",
        default=0)

    def __unicode__(self):
        return self.name

    def add_record(self, data):
        """
        Add new record
        :param data: Hash of field name -> value
        :type data: Dict
        """
        fields = {}
        for f in self.refbookfield_set.all():
            fields[f.name] = f.order - 1
        r = [None for f in range(len(fields))]
        for k, v in data.items():
            r[fields[k]] = v
        RefBookData(ref_book=self, value=r).save()

    def flush_refbook(self):
        """
        Delete all records in ref. book
        """
        RefBookData.objects.filter(ref_book=self).delete()

    def bulk_upload(self, data):
        """
        Bulk upload data to ref. book

        :param data: List of hashes field name -> value
        :type data: List
        """
        fields = {}
        for f in self.refbookfield_set.all():
            fields[f.name] = f.order - 1
        # Prepare empty row template
        row_template = [None for f in range(len(fields))]
        # Insert data
        for r in data:
            row = row_template[:]  # Clone template row
            for k, v in r.items():
                if k in fields:
                    row[fields[k]] = v
            RefBookData(ref_book=self, value=row).save()

    def download(self):
        """
        Download refbook
        """
        if self.downloader and self.downloader in downloader_registry.classes:
            downloader = downloader_registry[self.downloader]
            data = downloader.download(self)
            if data:
                self.flush_refbook()
                self.bulk_upload(data)
                self.last_updated = datetime.datetime.now()
                self.next_update = self.last_updated + datetime.timedelta(
                    days=self.refresh_interval)
                self.save()

    @property
    def can_search(self):
        """
        Check refbook has at least one searchable field
        """
        return self.refbookfield_set.filter(
            search_method__isnull=False).exists()

    @property
    def fields(self):
        """
        Get fields names sorted by order
        """
        return self.refbookfield_set.order_by("order")

# Circular references
from refbookdata import RefBookData
