# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Database triggers
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## NOC modules
from pyrule import PyRule


def model_choices():
    for m in models.get_models():
        yield (m._meta.db_table, m._meta.db_table)


class DBTrigger(models.Model):
    class Meta:
        app_label = "main"
        db_table = "main_dbtrigger"
        verbose_name = "Database Trigger"
        verbose_name_plural = "Database Triggers"
        ordering = ("model", "order")

    name = models.CharField("Name", max_length=64, unique=True)
    model = models.CharField("Model", max_length=128, choices=model_choices())
    is_active = models.BooleanField("Is Active", default=True)
    order = models.IntegerField("Order", default=100)
    description = models.TextField("Description", null=True, blank=True)
    pre_save_rule = models.ForeignKey(PyRule,
            verbose_name="Pre-Save Rule",
            related_name="dbtrigger_presave_set",
            limit_choices_to={"interface": "IDBPreSave"},
            blank=True, null=True)
    post_save_rule = models.ForeignKey(PyRule,
            verbose_name="Post-Save Rule",
            related_name="dbtrigger_postsave_set",
            limit_choices_to={"interface": "IDBPostSave"},
            blank=True, null=True)
    pre_delete_rule = models.ForeignKey(PyRule,
            verbose_name="Pre-Delete Rule",
            related_name="dbtrigger_predelete_set",
            limit_choices_to={"interface": "IDBPreDelete"},
            blank=True, null=True)
    post_delete_rule = models.ForeignKey(PyRule,
            verbose_name="Post-Delete Rule",
            related_name="dbtrigger_postdelete_set",
            limit_choices_to={"interface": "IDBPostDelete"},
            blank=True, null=True)
    ## State cache
    _pre_save_triggers = {}     # model.meta.db_table -> [rules]
    _post_save_triggers = {}    # model.meta.db_table -> [rules]
    _pre_delete_triggers = {}   # model.meta.db_table -> [rules]
    _post_delete_triggers = {}  # model.meta.db_table -> [rules]

    def __unicode__(self):
        return u"%s: %s" % (self.model, self.name)

    ##
    ## Refresh triggers cache
    ##
    @classmethod
    def refresh_cache(cls, *args, **kwargs):
        # Clear cache
        cls._pre_save_triggers = {}
        cls._post_save_triggers = {}
        cls._pre_delete_triggers = {}
        cls._post_delete_triggers = {}
        # Add all active triggers
        for t in cls.objects.filter(is_active=True).order_by("order"):
            for r in ["pre_save", "post_save", "pre_delete", "post_delete"]:
                c = getattr(cls, "_%s_triggers" % r)
                rule = getattr(t, "%s_rule" % r)
                if rule:
                    try:
                        c[t.model] += [rule]
                    except KeyError:
                        c[t.model] = [rule]

    ##
    ## Dispatcher for pre-save
    ##
    @classmethod
    def pre_save_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._pre_save_triggers:
            for t in cls._pre_save_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"])

    ##
    ## Dispatcher for post-save
    ##
    @classmethod
    def post_save_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._post_save_triggers:
            for t in cls._post_save_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"],
                  created=kwargs["created"])

    ##
    ## Dispatcher for pre-delete
    ##
    @classmethod
    def pre_delete_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._pre_delete_triggers:
            for t in cls._pre_delete_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"])

    ##
    ## Dispatcher for post-delete
    ##
    @classmethod
    def post_delete_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._post_delete_triggers:
            for t in cls._post_delete_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"])

    ##
    ## Called when all models are initialized
    ##
    @classmethod
    def x(cls):
        f = cls._meta.get_field_by_name("model")[0]
        f.choices = [(m._meta.db_table, m._meta.db_table)
            for m in models.get_models()]
