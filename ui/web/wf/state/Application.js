//---------------------------------------------------------------------
// wf.state application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.state.Application");

Ext.define("NOC.wf.state.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.wf.state.Model",
        "NOC.core.label.LabelField",
        "NOC.wf.workflow.LookupField",
        "NOC.main.remotesystem.LookupField",
        "Ext.ux.form.StringsField"
    ],
    model: "NOC.wf.state.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Workflow"),
                    dataIndex: "workflow",
                    renderer: NOC.render.Lookup("workflow"),
                    width: 150
                },
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Default"),
                    dataIndex: "is_default",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Productive"),
                    dataIndex: "is_productive",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Wiping"),
                    dataIndex: "is_wiping",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Update Last Seen"),
                    dataIndex: "is_productive",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Update Expired"),
                    dataIndex: "is_productive",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("TTL"),
                    dataIndex: "ttl",
                    width: 50,
                    align: "right",
                    renderer: NOC.render.Duration
                },
                {
                    text: __("Labels"),
                    dataIndex: "labels",
                    width: 200,
                    renderer: NOC.render.LabelField
                }
            ],

            fields: [
                {
                    name: "workflow",
                    xtype: "wf.workflow.LookupField",
                    fieldLabel: __("Workflow"),
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
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    query: {
                        "enable_workflowstate": true
                    },
                },
                {
                    name: "is_default",
                    xtype: "checkbox",
                    boxLabel: __("Default")
                },
                {
                    name: "is_productive",
                    xtype: "checkbox",
                    boxLabel: __("Productive")
                },
                {
                    name: "is_wiping",
                    xtype: "checkbox",
                    boxLabel: __("Wiping")
                },
                {
                    name: "update_last_seen",
                    xtype: "checkbox",
                    boxLabel: __("Update Last Seen")
                },
                {
                    name: "ttl",
                    xtype: "numberfield",
                    fieldLabel: __("TTL"),
                    allowBlank: true,
                    minValue: 0,
                    emptyText: __("Not Limited"),
                    uiStyle: "medium"
                },
                {
                    name: "update_expired",
                    xtype: "checkbox",
                    boxLabel: __("Update Expiration")
                },
                {
                    name: "feature_settings",
                    xtype: "gridfield",
                    fieldLabel: __("Features"),
                    columns: [
                        {
                            text: __("Feature"),
                            dataIndex: "feature",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["SA", "SA"],
                                    ["FM", "FM"],
                                    ["TT", "TT"]
                                ]
                            }
                        },
                        {
                            text: __("Enable"),
                            dataIndex: "enable",
                            editor: "checkbox",
                            renderer: NOC.render.Bool,
                            flex: 1
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
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
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    name: "on_enter_handlers",
                    xtype: "stringsfield",
                    fieldLabel: __("On Enter Handlers"),
                    allowBlank: true
                },
                {
                    name: "on_leave_handlers",
                    xtype: "stringsfield",
                    fieldLabel: __("On Leave Handlers"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    },
    filters: [
        {
            title: __("By Workflow"),
            name: "workflow",
            ftype: "lookup",
            lookup: "wf.workflow"
        },
        {
            title: __("By Default"),
            name: "is_default",
            ftype: "boolean"
        },
        {
            title: __("By Productive"),
            name: "is_productive",
            ftype: "boolean"
        }
    ]
});
