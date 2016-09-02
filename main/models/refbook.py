# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Database triggers
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## Django modules
from django.db import models
from noc.main.refbooks.downloaders import downloader_registry
from noc.core.model.fields import TextArrayField

rx_mac_3_octets = re.compile("^([0-9A-F]{6}|[0-9A-F]{12})$", re.IGNORECASE)
downloader_registry.register_all()


class RefBook(models.Model):
    """
    Reference Books
    """

    class Meta:
        verbose_name = "Ref Book"
        verbose_name_plural = "Ref Books"

    name = models.CharField("Name", max_length=128, unique=True)
    language = models.ForeignKey("main.Language", verbose_name="Language")
    description = models.TextField("Description", blank=True, null=True)
    is_enabled = models.BooleanField("Is Enabled", default=False)
    is_builtin = models.BooleanField("Is Builtin", default=False)
    downloader = models.CharField("Downloader", max_length=64,
                                  choices=downloader_registry.choices, blank=True, null=True)
    download_url = models.CharField("Download URL",
                                    max_length=256, null=True, blank=True)
    last_updated = models.DateTimeField("Last Updated", blank=True, null=True)
    next_update = models.DateTimeField("Next Update", blank=True, null=True)
    refresh_interval = models.IntegerField("Refresh Interval (days)", default=0)

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
                self.next_update = self.last_updated + datetime.timedelta(days=self.refresh_interval)
                self.save()

    @property
    def can_search(self):
        """
        Check refbook has at least one searchable field
        """
        return self.refbookfield_set.filter(search_method__isnull=False).exists()

    @property
    def fields(self):
        """
        Get fields names sorted by order
        """
        return self.refbookfield_set.order_by("order")


class RBDManader(models.Manager):
    """
    Ref Book Data Manager
    """

    # Order by first field
    def get_query_set(self):
        return super(RBDManader, self).get_query_set().extra(order_by=["main_refbookdata.value[1]"])


class RefBookData(models.Model):
    """
    Ref. Book Data
    """

    class Meta:
        verbose_name = "Ref Book Data"
        verbose_name_plural = "Ref Book Data"

    ref_book = models.ForeignKey(RefBook, verbose_name="Ref Book")
    value = TextArrayField("Value")

    objects = RBDManader()

    def __unicode__(self):
        return u"%s: %s" % (self.ref_book, self.value)

    @property
    def items(self):
        """
        Returns list of pairs (field,data)
        """
        return zip(self.ref_book.fields, self.value)


class RefBookField(models.Model):
    """
    Refbook fields
    """

    class Meta:
        verbose_name = "Ref Book Field"
        verbose_name_plural = "Ref Book Fields"
        unique_together = [("ref_book", "order"), ("ref_book", "name")]
        ordering = ["ref_book", "order"]

    ref_book = models.ForeignKey(RefBook, verbose_name="Ref Book")
    name = models.CharField("Name", max_length="64")
    order = models.IntegerField("Order")
    is_required = models.BooleanField("Is Required", default=True)
    description = models.TextField("Description", blank=True, null=True)
    search_method = models.CharField("Search Method", max_length=64,
                                     blank=True, null=True,
                                     choices=[
                                         ("string", "string"),
                                         ("substring", "substring"),
                                         ("starting", "starting"),
                                         ("mac_3_octets_upper", "3 Octets of the MAC")])

    def __unicode__(self):
        return u"%s: %s" % (self.ref_book, self.name)

    # Return **kwargs for extra
    def get_extra(self, search):
        if self.search_method:
            return getattr(self, "search_%s" % self.search_method)(search)
        else:
            return {}

    def search_string(self, search):
        """
        string search method
        """
        return {
            "where": ["value[%d] ILIKE %%s" % self.order],
            "params": [search]
        }

    def search_substring(self, search):
        """
        substring search method
        """
        return {
            "where": ["value[%d] ILIKE %%s" % self.order],
            "params": ["%" + search + "%"]
        }

    def search_starting(self, search):
        """
        starting search method
        """
        return {
            "where": ["value[%d] ILIKE %%s" % self.order],
            "params": [search + "%"]
        }

    def search_mac_3_octets_upper(self, search):
        """
        Match 3 first octets of the MAC address
        """
        mac = search.replace(":", "").replace("-", "").replace(".", "")
        if not rx_mac_3_octets.match(mac):
            return {}
        return {
            "where": ["value[%d]=%%s" % self.order],
            "params": [mac]
        }
