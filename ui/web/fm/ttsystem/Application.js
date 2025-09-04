//---------------------------------------------------------------------
// fm.ttsystem application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.ttsystem.Application");

Ext.define("NOC.fm.ttsystem.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.ttsystem.Model",
        "NOC.main.remotesystem.LookupField"
    ],
    model: "NOC.fm.ttsystem.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 100
                },
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Handler"),
                    dataIndex: "handler",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    fieldLabel: __("Active"),
                    allowBlank: false
                },
                {
                    name: "handler",
                    xtype: "textfield",
                    fieldLabel: __("Handler"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "connection",
                    xtype: "textfield",
                    fieldLabel: __("Connection"),
                    allowBlank: false
                },
                {
                    name: "login",
                    xtype: "textfield",
                    fieldLabel: __("Login"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "shard_name",
                    xtype: "textfield",
                    fieldLabel: __("Shard"),
                    regex: /^[0-9a-zA-z]{1,16}$/,
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "max_threads",
                    xtype: "numberfield",
                    fieldLabel: __("Max. Threads"),
                    allowBlank: false,
                    min: 0,
                    uiStyle: "small"
                },
                {
                    name: "failure_cooldown",
                    xtype: "numberfield",
                    fieldLabel: __("Failure Cooldown"),
                    allowBlank: true,
                    min: 0,
                    uiStyle: "small"
                },
                {
                    name: "alarm_consequence_policy",
                    xtype: "combobox",
                    fieldLabel: __("Escalate Alarm Consequence Policy"),
                    allowBlank: false,
                    queryMode: "local",
                    displayField: "label",
                    valueField: "id",
                    store: {
                        fields: ["id", "label"],
                        data: [
                            {id: "D", label: "Disable"},
                            {id: "a", label: "Escalate with alarm timestamp"},
                            {id: "c", label: "Escalate with current timestamp"}]
                    },
                    uiStyle: "medium"
                },
                {
                    name: "promote_items",
                    xtype: "combobox",
                    fieldLabel: __("Escalate Items Add Policy"),
                    allowBlank: false,
                    queryMode: "local",
                    displayField: "label",
                    valueField: "id",
                    store: {
                        fields: ["id", "label"],
                        data: [
                            {id: "D", label: "Disable"},
                            {id: "T", label: "Items with TTSystem set"},
                            {id: "R", label: "Items with RemoteSystem set"},
                            {id: "I", label: "Any Items"}]
                    },
                    uiStyle: "medium"
                },
                {
                    name: "telemetry_sample",
                    xtype: "numberfield",
                    fieldLabel: __("Tememetry Sample"),
                    allowBlank: false,
                    min: 0,
                    uiStyle: "small"
                },
                {
                    name: "check_updates_interval",
                    xtype: "numberfield",
                    fieldLabel: __("Check Updates Interval"),
                    allowBlank: true,
                    min: 0,
                    uiStyle: "small"
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
                }
            ]
        });
        me.callParent();
    }
});
