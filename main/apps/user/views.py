# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## User Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
## NOC modules
from noc.lib.app import ModelApplication, view
from noc.main.models import Permission
from widgets import AccessWidget


class UserChangeForm(forms.ModelForm):
    username = forms.RegexField(label=_("Username"), max_length=75, regex=r"^[\w.@+-]+$",
        help_text=_("Required. 75 characters or fewer.  Letters, digits and @/./+/-/_ only"),
        error_message=_("This value must contain only letters, digits and @/./+/-/_."))
    noc_user_permissions = forms.CharField(label="User Access", widget=AccessWidget, required=False)

    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        if "instance" in kwargs:
            self.initial["noc_user_permissions"] = "user:" + self.initial["username"]
        self.new_perms = set()
        if args:
            self.new_perms = set([p[5:] for p in args[0] if p.startswith("perm_")])

    def save(self, commit=True):
        model = super(UserChangeForm, self).save(commit)
        model.is_staff = True
        #if not model.id:
        model.save()
        Permission.set_user_permissions(model, self.new_perms)
        return model


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('User category'), {'fields': ('is_active', 'is_superuser')}),
        (_('Groups'), {'fields': ('groups',)}),
        (_('Access'), {'fields': ('noc_user_permissions',), "classes": ["collapse"]}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )
    list_display = ('username', 'email', 'first_name', 'last_name', "is_active", "is_superuser")
    list_filter = ('is_superuser', 'is_active')
    filter_horizontal = ("groups",)
    form = UserChangeForm


class UserApplication(ModelApplication):
    model = User
    model_admin = UserAdmin
    menu = "Setup | Users"
    icon = "icon_user"
    title = "Users"

    @view(url=r"^(\d+)/password/$", method=["GET", "POST"], access="change")
    def view_change_password(self, request, object_id):
        """
        Change user's password
        :param request:
        :param object_id:
        :return:
        """
        if not self.admin.has_change_permission(request):
            return self.response_fobidden("Permission denied")
        user = get_object_or_404(self.model, pk=object_id)
        if request.POST:
            form = self.admin.change_password_form(user, request.POST)
            if form.is_valid():
                new_user = form.save()
                self.message_user(request, "Password changed")
                return self.response_redirect("main:user:change", object_id)
        else:
            form = self.admin.change_password_form(user)
        return self.render(request, "change_password.html",
            form=form, original=user)

    def has_delete_permission(self, request, obj=None):
        """Disable 'Delete' button"""
        return False
    
