//---------------------------------------------------------------------
// inv.platform application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.platform.Application");

Ext.define("NOC.inv.platform.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.platform.Model",
        "NOC.inv.vendor.LookupField"
    ],
    model: "NOC.inv.platform.Model",
    search: true,

    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/inv/platform/{id}/json/'),
            previewName: new Ext.XTemplate('Platform: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    flex: 1
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    width: 30,
                    renderer: NOC.render.Bool,
                    sortable: false
                }
            ],

            fields: [
                {
                    name: "vendor",
                    xtype: "inv.vendor.LookupField",
                    fieldLabel: __("Platform"),
                    allowBlank: false
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
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
                    allowBlank: false
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
