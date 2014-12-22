//---------------------------------------------------------------------
// Link Interfaces window
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.ChangeInterfaceProfileForm");

Ext.define("NOC.inv.interface.ChangeInterfaceProfileForm", {
    extend: "Ext.Window",
    requires: [
        "NOC.inv.interfaceprofile.LookupField"
    ],
    autoShow: true,
    closable: true,
    maximizable: true,
    modal: true,
    // width: 300,
    // height: 200,
    autoScroll: true,
    layout: "fit",

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            autoLoad: false,
            fields: ["id", "label"],
            data: []
        });

        Ext.apply(me, {
            title: "Change " + me.record.get("name") + " profile",
            items: [
                {
                    xtype: "form",
                    items: [
                        {
                            xtype: "inv.interfaceprofile.LookupField",
                            name: "profile",
                            fieldLabel: "Profile",
                            allowBlank: false
                        }
                    ],
                    buttonAlign: "center",
                    buttons: [
                        {
                            text: "Change",
                            glyph: NOC.glyph.check,
                            formBind: true,
                            scope: me,
                            handler: me.onChangeProfile
                        }
                    ]
                }
            ]
        });
        me.callParent();
        me.field = me.items.first().getForm().getFields().items[0];
    },
    //
    onChangeProfile: function() {
        var me = this,
            profile = me.field.getValue(),
            profile_label = me.field.getDisplayValue(),
            data = {
                profile: profile
            };

        Ext.Ajax.request({
            url: "/inv/interface/l1/" + me.record.get("id") + "/change_profile/",
            method: "POST",
            jsonData: data,
            scope: me,
            success: function() {
                me.record.set("profile", profile);
                me.record.set("profile__label", profile_label);
                me.close();
            },
            failure: function() {
                NOC.error("Failed to change profile");
            }
        });
    }
});
