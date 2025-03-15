//---------------------------------------------------------------------
// inv.macblacklist application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.macblacklist.Application");

Ext.define("NOC.inv.macblacklist.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.macblacklist.Model",
        "NOC.inv.vendor.LookupField",
        "NOC.inv.platform.LookupField"
    ],
    model: "NOC.inv.macblacklist.Model",
    search: true,
    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/inv/macblacklist/{id}/json/'),
            previewName: new Ext.XTemplate('MAC Blacklist: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("From"),
                    dataIndex: "from_mac",
                    width: 150
                },
                {
                    text: __("To"),
                    dataIndex: "to_mac",
                    width: 150
                },
                {
                    text: __("Duplicate"),
                    dataIndex: "is_duplicated",
                    width: 50,
                    renderer: NOC.render.Bool
                }
            ],

            fields: [
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
                    fieldLabel: __("UUID"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    xtype: "container",
                    layout: "hbox",
                    defaults: {
                        padding: 4
                    },
                    items: [
                        {
                            name: "from_mac",
                            xtype: "textfield",
                            fieldLabel: __("From"),
                            uiStyle: "medium",
                            allowBlank: false
                        },
                        {
                            name: "to_mac",
                            xtype: "textfield",
                            fieldLabel: __("To"),
                            uiStyle: "medium",
                            allowBlank: false
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Reason"),
                    defaults: {
                        padding: 4
                    },
                    items: [
                        {
                            name: "is_duplicated",
                            xtype: "checkbox",
                            boxLabel: __("Duplicated")
                        },
                        {
                            name: "is_ignored",
                            xtype: "checkbox",
                            boxLabel: __("Ignored")
                        }
                    ]
                },
                {
                    name: "affected",
                    xtype: "gridfield",
                    fieldLabel: __("Affected"),
                    columns: [
                        {
                            text: __("Vendor"),
                            dataIndex: "vendor",
                            editor: "inv.vendor.LookupField",
                            width: 200,
                            renderer: NOC.render.Lookup("vendor")
                        },
                        {
                            text: __("Platform"),
                            dataIndex: "platform",
                            editor: "inv.platform.LookupField",
                            width: 200,
                            renderer: NOC.render.Lookup("platform")
                        }
                    ]
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

    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});