//---------------------------------------------------------------------
// sa.service application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.Application");

Ext.define("NOC.sa.service.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.service.Model",
        "NOC.sa.service.LookupField",
        "NOC.sa.serviceprofile.LookupField",
        "NOC.crm.subscriber.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.sa.managedobject.LookupField"
    ],
    model: "NOC.sa.service.Model",
    search: true,

    initComponent: function () {
        var me = this;

        Ext.apply(me, {
            columns: [
                {
                    text: __("ID"),
                    dataIndex: "id",
                    width: 160
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 200,
                    renderer: NOC.render.Lookup("profile")
                },
                {
                    text: __("Subscriber"),
                    dataIndex: "subscriber",
                    width: 250,
                    renderer: NOC.render.Lookup("subscriber")
                },
                {
                    text: __("Logical Status"),
                    dataIndex: "logical_status",
                    width: 120,
                    renderer: NOC.render.Choices({
                        P: __("Planned"),
                        p: __("Provisioning"),
                        T: __("Testing"),
                        R: __("Ready"),
                        S: __("Suspended"),
                        r: __("Removing"),
                        C: __("Closed"),
                        U: __("Unknown")
                    })
                },
                {
                    text: __("Parent"),
                    dataIndex: "parent",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "profile",
                    xtype: "sa.serviceprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: false
                },
                {
                    name: "logical_status",
                    xtype: "combobox",
                    fieldLabel: __("Logical Status"),
                    allowBlank: false,
                    store: [
                        ["P", "Planned"],
                        ["p", "Provisioning"],
                        ["T", "Testing"],
                        ["R", "Ready"],
                        ["S", "Suspended"],
                        ["r", "Removing"],
                        ["C", "Closed"],
                        ["U", "Unknown"]
                    ],
                    uiStyle: "medium"
                },
                {
                    name: "parent",
                    xtype: "sa.service.LookupField",
                    fieldLabel: __("Parent"),
                    allowBlank: true
                },
                {
                    name: "subscriber",
                    xtype: "crm.subscriber.LookupField",
                    fieldLabel: __("Subscriber"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "agreement_id",
                    xtype: "textfield",
                    fieldLabel: __("Agreement ID"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "address",
                    xtype: "textfield",
                    fieldLabel: __("Address"),
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Network Resources"),
                    defaults: {
                        padding: 4,
                        labelAlign: "top"
                    },
                    items: [
                        {
                            name: "managed_object",
                            xtype: "sa.managedobject.LookupField",
                            fieldLabel: __("Managed Object"),
                            allowBlank: true
                        },
                        {
                            name: "nri_port",
                            xtype: "textfield",
                            fieldLabel: __("NRI Port"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("CPE"),
                    defaults: {
                        padding: 4,
                        labelAlign: "top"
                    },
                    items: [
                        {
                            name: "cpe_serial",
                            xtype: "textfield",
                            fieldLabel: __("Serial"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "cpe_mac",
                            xtype: "textfield",
                            fieldLabel: __("MAC"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "top"
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "bi_id",
                            xtype: "textfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },

    filters: [
        {
            title: __("By Profile"),
            name: "profile",
            ftype: "lookup",
            lookup: "sa.serviceprofile"
        },
        {
            title: __("By Subscriber"),
            name: "subscriber",
            ftype: "lookup",
            lookup: "crm.subscriber"
        },
        {
            title: __("By State"),
            name: "logical_status",
            ftype: "choices",
            store: [
                ["P", "Planned"],
                ["p", "Provisioning"],
                ["T", "Testing"],
                ["R", "Ready"],
                ["S", "Suspended"],
                ["r", "Removing"],
                ["C", "Closed"],
                ["U", "Unknown"]
            ]
        }
    ],

    levelFilter: {
        icon: NOC.glyph.level_down,
        color: NOC.colors.level_down,
        filter: 'parent',
        tooltip: __('Parent Filter')
    },

    onPreview: function(record) {
        window.open(
            "/api/card/view/service/"
            + record.get("id")
            + "/"
        )
    }
});
