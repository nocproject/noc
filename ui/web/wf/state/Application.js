//---------------------------------------------------------------------
// wf.state application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.state.Application");

Ext.define("NOC.wf.state.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.wf.state.Model",
        "NOC.core.JSONPreview",
        "NOC.core.label.LabelField",
        "NOC.wf.workflow.LookupField",
        "NOC.main.remotesystem.LookupField",
        "Ext.ux.form.StringsField"
    ],
    model: "NOC.wf.state.Model",
    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/wf/state/{id}/json/'),
            previewName: new Ext.XTemplate('Workflow State: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

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
                    text: __("Hide Records"),
                    dataIndex: "hide_with_state",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Update Last Seen"),
                    dataIndex: "update_last_seen",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Update Expired"),
                    dataIndex: "update_expired",
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
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    query: {
                        "allow_models": ["wf.WorkflowState"]
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
                    name: "hide_with_state",
                    xtype: "checkbox",
                    boxLabel: __("Hide Records")
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
                    name: "disable_all_interaction",
                    xtype: "checkbox",
                    boxLabel: __("Disable All Interaction")
                },
                {
                    name: "interaction_settings",
                    xtype: "gridfield",
                    fieldLabel: __("Interaction Settings"),
                    columns: [
                        {
                            text: __("Interaction"),
                            dataIndex: "interaction",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["SA", "ServiceActivation"],
                                    ["ALARM", "Alarm"],
                                    ["EVENT", "Event"],
                                    ["TT", "Escalation"],
                                    ["BOX", "Box Discovery"],
                                    ["PERIODIC", "Periodic Discovery"]
                                ]
                            },
                            renderer: NOC.render.Choices({
                                "SA": __("ServiceActivation"),
                                "ALARM": __("Alarm"),
                                "EVENT": __("Event"),
                                "TT": __("Escalation"),
                                "BOX": __("Box Discovery"),
                                "PERIODIC": __("Periodic Discovery")
                            })
                        },
                        {
                            text: __("Enable"),
                            dataIndex: "enable",
                            editor: "checkbox",
                            renderer: NOC.render.Bool,
                            width: 50,
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
