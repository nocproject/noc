//---------------------------------------------------------------------
// inv.firmware application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.firmware.Application");

Ext.define("NOC.inv.firmware.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.firmware.Model",
        "NOC.inv.vendor.LookupField",
        "NOC.sa.profile.LookupField"
    ],
    model: "NOC.inv.firmware.Model",
    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/inv/firmware/{id}/json/'),
            previewName: new Ext.XTemplate('Firmware: {version}')
        });

        Ext.apply(me, {
            columns: [
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 100,
                    renderer: NOC.render.Lookup("profile")
                },
                {
                    text: __("Vendor"),
                    dataIndex: "vendor",
                    width: 100,
                    renderer: NOC.render.Lookup("vendor")
                },
                {
                    text: __("Version"),
                    dataIndex: "version",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "profile",
                    xtype: "sa.profile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: false
                },
                {
                    name: "vendor",
                    xtype: "inv.vendor.LookupField",
                    fieldLabel: __("Vendor"),
                    allowBlank: false
                },
                {
                    name: "version",
                    xtype: "textfield",
                    fieldLabel: __("Version"),
                    allowBlank: false
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "download_url",
                    xtype: "textfield",
                    fieldLabel: __("URL"),
                    allowBlank: true
                }
            ],

            formToolbar: [
                {
                    text: __("JSON"),
                    glyph: NOC.glyph.file,
                    tooltip: __("Show JSON"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                }
            ]
        });
        me.callParent();
    },

    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
