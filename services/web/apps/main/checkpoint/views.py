# ---------------------------------------------------------------------
# Checkpoint manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from django import forms

# NOC modules
from noc.services.web.base.application import Application, view, HasPerm
from noc.core.forms import NOCForm
from noc.main.models.checkpoint import Checkpoint
from noc.core.translation import ugettext as _


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
                Checkpoint.set_checkpoint(
                    comment=form.cleaned_data["comment"],
                    user=request.user,
                    timestamp=datetime.datetime.now(),
                    private=form.cleaned_data.get("is_private", False),
                )
                self.message_user(request, _("Checkpoint has been set"))
                return self.close_popup(request)
        else:
            form = form_class({"is_private": True})
        return self.render(request, "create.html", form=form)
