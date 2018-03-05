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

    initComponent: function () {
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
                    text: __("Vendor"),
                    dataIndex: "vendor",
                    width: 150,
                    renderer: NOC.render.Lookup("vendor")
                },
                {
                    text: __("Platform"),
                    dataIndex: "full_name",
                    flex: 1
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    width: 30,
                    renderer: NOC.render.Bool,
                    sortable: false
                },
                {
                    text: __("sysObjectID"),
                    dataIndex: "snmp_sysobjectid",
                    width: 200
                },
                {
                    text: __("Start of Sale"),
                    dataIndex: "start_of_sale",
                    width: 150
                },
                {
                    text: __("End of Sale"),
                    dataIndex: "end_of_sale",
                    width: 150
                },
                {
                    text: __("End of Support"),
                    dataIndex: "end_of_support",
                    width: 150
                },
                {
                    text: __("End of Extended Support"),
                    dataIndex: "end_of_xsupport",
                    width: 150
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
                    fieldLabel: __("UUID"),
                    allowBlank: true
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    title: __("Support"),
                    items: [
                        {
                            name: "start_of_sale",
                            xtype: "datefield",
                            startDay: 1,
                            fieldLabel: __("Start of Sale"),
                            allowBlank: true,
                            uiStyle: "medium",
                            format: "Y-m-d"
                        },
                        {
                            name: "end_of_sale",
                            xtype: "datefield",
                            startDay: 1,
                            fieldLabel: __("End of Sale"),
                            allowBlank: true,
                            uiStyle: "medium",
                            format: "Y-m-d"
                        },
                        {
                            name: "end_of_support",
                            xtype: "datefield",
                            startDay: 1,
                            fieldLabel: __("End of Support"),
                            allowBlank: true,
                            uiStyle: "medium",
                            format: "Y-m-d"
                        },
                        {
                            name: "end_of_xsupport",
                            xtype: "datefield",
                            startDay: 1,
                            fieldLabel: __("End of Extended Support"),
                            allowBlank: true,
                            uiStyle: "medium",
                            format: "Y-m-d"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("SNMP OID"),
                    items: [
                        {
                            name: "snmp_sysobjectid",
                            xtype: "textfield",
                            fieldLabel: "sysObjectID.0",
                            allowBlank: true,
                            regex: /^1.3.6(\.\d+)+$/,
                            uiStyle: "large"
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
            ],

            filters: [
                {
                    title: __("By Vendor"),
                    name: "vendor",
                    ftype: "lookup",
                    lookup: "inv.vendor"
                }
            ]
        });
        me.callParent();
    },

    onJSON: function () {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
