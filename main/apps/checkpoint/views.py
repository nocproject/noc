# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Checkpoint manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django.utils.translation import ugettext_lazy as _
from django import forms
## NOC modules
from noc.lib.app import Application, view, HasPerm
from noc.lib.forms import NOCForm
from noc.main.models import Checkpoint

class CheckpointAppplication(Application):
    title = _("Checkpoints")
    
    class PrivateCheckpointForm(NOCForm):
        comment = forms.CharField(label=_("Comment"))
    
    class FullCheckpointForm(NOCForm):
        comment = forms.CharField(label=_("Comment"))
        is_private = forms.BooleanField(label=_("Private"), required=False)

    @view(url="^create/$", url_name="create", access=HasPerm("create"))
    def view_create(self, request):
        if request.user.is_superuser:
            form_class = self.FullCheckpointForm
        else:
            form_class = self.PrivateCheckpointForm
        if request.POST:
            form = form_class(request.POST)
            if form.is_valid():
                Checkpoint.set_checkpoint(comment=form.cleaned_data["comment"],
                                          user=request.user,
                                          timestamp=datetime.datetime.now(),
                                          private=form.cleaned_data.get("is_private", False))
                self.message_user(request, _("Checkpoint has been set"))
                return self.close_popup(request)
        else:
            form = form_class({"is_private": True})
        return self.render(request, "create.html", form=form)
