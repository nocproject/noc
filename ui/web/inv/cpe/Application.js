//---------------------------------------------------------------------
// inv.cpe application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.cpe.Application");

Ext.define("NOC.inv.cpe.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.StateField",
        "NOC.inv.cpe.Model",
        "NOC.inv.cpeprofile.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.sa.managedobject.LookupField",
        "NOC.inv.capability.LookupField",
        "NOC.inv.resourcegroup.LookupField",
        "NOC.core.label.LabelField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.inv.cpe.Model",
    search: true,
    helpId: "reference-cpe",

    initComponent: function () {
        var me = this;

        Ext.apply(me, {
            columns: [
                {
                    text: __("Global ID"),
                    dataIndex: "global_id",
                    width: 160
                },
                {
                    text: __("Label"),
                    dataIndex: "label",
                    width: 160
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 150,
                    renderer: NOC.render.Lookup("profile")
                },
                {
                    text: __("State"),
                    dataIndex: "state",
                    width: 200,
                    renderer: NOC.render.Lookup("state")
                },
                {
                    text: __("Controller"),
                    dataIndex: "controller",
                    renderer: NOC.render.Lookup("controller"),
                    width: 160
                },
                {
                    text: __("Local ID"),
                    dataIndex: "local_id",
                    width: 160
                },
                {
                    text: __("Oper Status."),
                    dataIndex: "oper_status",
                    width: 60,
                    renderer: NOC.render.Bool,
                    sortable: false
                }
            ],

            fields: [
                {
                    name: "profile",
                    xtype: "inv.cpeprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: false
                },
                {
                    name: "state",
                    xtype: "statefield",
                    fieldLabel: __("State"),
                    allowBlank: true
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    query: {
                        "allow_models": ["inv.CPE"]
                    },
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "global_id",
                    xtype: "textfield",
                    fieldLabel: __("Global Id"),
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
                            name: "controller",
                            xtype: "sa.managedobject.LookupField",
                            fieldLabel: __("Managed Object"),
                            allowBlank: true
                        },
                        {
                            name: "local_id",
                            xtype: "textfield",
                            fieldLabel: __("Local Id"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    name: "bi_id",
                    xtype: "displayfield",
                    fieldLabel: __("BI ID"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                //{
                //    xtype: "fieldset",
                //    title: __("Resource Groups"),
                //    layout: "column",
                //    minWidth: me.formMinWidth,
                //    maxWidth: me.formMaxWidth,
                //    defaults: {
                //        columnWidth: 0.5,
                //        padding: 10
                //    },
                //    collapsible: true,
                //    collapsed: false,
                //    items: [
                //        {
                //            name: "static_service_groups",
                //            xtype: "gridfield",
                //            columns: [
                //                {
                //                    dataIndex: "group",
                //                    text: __("Static Service Groups"),
                //                    width: 350,
                //                    renderer: NOC.render.Lookup("group"),
                //                    editor: {
                //                        xtype: "inv.resourcegroup.LookupField"
                //                    }
                //                }
                //            ]
                //        },
                //        {
                //            name: "effective_service_groups",
                //            xtype: "gridfield",
                //            columns: [
                //                {
                //                    dataIndex: "group",
                //                    text: __("Effective Service Groups"),
                //                    width: 350,
                //                    renderer: NOC.render.Lookup("group"),
                //                    editor: {
                //                        xtype: "inv.resourcegroup.LookupField"
                //                    }
                //                }
                //            ]
                //        },
                //        {
                //            name: "static_client_groups",
                //            xtype: "gridfield",
                //            columns: [
                //                {
                //                    dataIndex: "group",
                //                    text: __("Static Client Groups"),
                //                    width: 350,
                //                    renderer: NOC.render.Lookup("group"),
                //                    editor: {
                //                        xtype: "inv.resourcegroup.LookupField"
                //                    }
                //                }
                //            ]
                //        },
                //        {
                //            name: "effective_client_groups",
                //            xtype: "gridfield",
                //            columns: [
                //                {
                //                    dataIndex: "group",
                //                    text: __("Effective Client Groups"),
                //                    width: 350,
                //                    renderer: NOC.render.Lookup("group"),
                //                    editor: {
                //                        xtype: "inv.resourcegroup.LookupField"
                //                    }
                //                }
                //            ]
                //        }
                //    ]
                //},
                {
                    name: "controllers",
                    xtype: "gridfield",
                    fieldLabel: __("Controllers"),
                    allowBlank: true,
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "managed_object",
                            renderer: NOC.render.Lookup("managed_object"),
                            width: 250,
                            editor: "sa.managed_object.LookupField"
                        },
                        {
                            text: __("LocalID"),
                            dataIndex: "local_id",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: __("Active"),
                            dataIndex: "is_active",
                            width: 25,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Interface"),
                            dataIndex: "interface",
                            width: 100,
                            editor: "textfield"
                        }
                    ]
                },
                {
                    name: "caps",
                    xtype: "gridfield",
                    fieldLabel: __("Capabilities"),
                    allowBlank: true,
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "capability",
                            renderer: NOC.render.Lookup("capability"),
                            width: 250,
                            editor: "inv.capability.LookupField"
                        },
                        {
                            text: __("Value"),
                            dataIndex: "value",
                            flex: 1,
                            editor: "textfield"
                        },
                        {
                            text: __("Source"),
                            dataIndex: "source",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: __("Scope"),
                            dataIndex: "scope",
                            width: 50,
                            editor: "textfield"
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
            lookup: "inv.cpeprofile"
        },
        {
            title: __("By State"),
            name: "state",
            ftype: "lookup",
            lookup: "wf.state"
        },
        {
            title: __("By Object"),
            name: "controller",
            ftype: "lookup",
            lookup: "sa.managedobject"
        }
    ],

    onPreview: function(record) {
        window.open(
            "/api/card/view/cpe/"
            + record.get("id")
            + "/"
        )
    }
});
