//---------------------------------------------------------------------
// ip.ipam.vrf form
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.vrf.VRFController");

Ext.define("NOC.ip.ipam.view.forms.vrf.VRFController", {
    extend: "Ext.app.ViewController",
    alias: "controller.ip.ipam.form.vrf",
    //
    onClose: function() {
        this.fireViewEvent("ipIPAMVRFCloseForm");
    },
    onSave: function() {
        var me = this,
            source = me.getView().up("[itemId=ip-ipam]").getViewModel().data.vrf,
            data = me.serialize(source);
        me.getView().mask(__("Saving..."));
        delete source["state"];
        delete source["state__label"];
        delete source["profile__label"];
        delete source["vrf_group__label"];
        delete source["project__label"];
        Ext.Ajax.request({
            url: "/ip/vrf/" + source.id + "/",
            method: "PUT",
            jsonData: Ext.merge(source, data),
            success: function(response) {
                me.getView().unmask();
                if(response.status === 200) {
                    NOC.msg.complete(__("Saved"));
                }
                me.onClose();
            },
            failure: function() {
                me.getView().unmask();
                NOC.error(__("Failed to save"));
                me.onClose();
            }
        });
    },
    serialize: function(value) {
        var me = this,
            data = {},
            allocatedTill = "allocated_till",
            getComboValue = function(name) {
                data[name] = me.getView().down("[name=" + name + "]").getValue();
            };
        // combos
        Ext.each([
            "profile",
            "vrf_group",
            "project"
        ], getComboValue, this);
        data[allocatedTill] = this.getView().down("[name=" + allocatedTill + "]").getSubmitValue();
        return data;
    }
});
