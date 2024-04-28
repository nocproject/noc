//---------------------------------------------------------------------
// fm.escalationprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.escalationprofile.Application");

Ext.define("NOC.fm.escalationprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.escalationprofile.Model",
        "NOC.fm.ttsystem.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.notificationgroup.LookupField",
        "NOC.main.timepattern.LookupField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.fm.escalationprofile.Model",
    initComponent: function () {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 250
                },
                {
                    text: __('Description'),
                    dataIndex: 'description',
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
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "escalation_policy",
                    xtype: "combobox",
                    fieldLabel: __("Group Escalation Policy"),
                    allowBlank: false,
                    queryMode: "local",
                    displayField: "label",
                    valueField: "id",
                    store: {
                        fields: ["id", "label"],
                        data: [
                            {id: "0", label: "Never Items"},
                            {id: "1", label: "Start From Root"},
                            {id: "2", label: "Only if Root"},
                            {id: "3", label: "From First"},
                            {id: "4", label: "Current Alarm"},
                            ]
                    },
                    uiStyle: "medium"
                },
                {
                    name: "maintenance_policy",
                    xtype: "combobox",
                    fieldLabel: __("Escalate Maintenance Policy"),
                    allowBlank: false,
                    queryMode: "local",
                    displayField: "label",
                    valueField: "id",
                    store: {
                        fields: ["id", "label"],
                        data: [
                            {id: "w", label: "Wait End Maintenance"},
                            {id: "i", label: "Ignore Maintenance"},
                            {id: "e", label: "End Escalation"}]
                    },
                    uiStyle: "medium"
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
                    name: "end_condition",
                    xtype: "combobox",
                    fieldLabel: __("End Condition"),
                    allowBlank: false,
                    queryMode: "local",
                    displayField: "label",
                    valueField: "id",
                    store: {
                        fields: ["id", "label"],
                        data: [
                            {id: "CR", label: "Close Root"},
                            {id: "CA", label: "Close All"},
                            {id: "E", label: "End Escalation"},
                            {id: "CT", label: "Close TT"},
                            {id: "M", label: "Manual"}]
                    },
                    uiStyle: "medium"
                },
                {
                    name: "escalations",
                    xtype: "gridfield",
                    fieldLabel: __("Escalations"),
                    columns: [
                        {
                            text: __("Delay"),
                            dataIndex: "delay",
                            editor: "numberfield",
                            width: 75
                        },
                        {
                            text: __("Time Pattern"),
                            dataIndex: "time_pattern",
                            editor: "main.timepattern.LookupField",
                            renderer: NOC.render.Lookup("time_pattern")
                        },
                        {
                            text: __("Severity"),
                            dataIndex: "min_severity",
                            editor: "numberfield",
                            width: 70
                        },
                        {
                            text: __("Notification Group"),
                            dataIndex: "notification_group",
                            editor: "main.notificationgroup.LookupField",
                            width: 150,
                            renderer: NOC.render.Lookup("notification_group")
                        },
                        {
                            text: __("Open Template"),
                            dataIndex: "template",
                            editor: "main.template.LookupField",
                            width: 100,
                            renderer: NOC.render.Lookup("template")
                        },
                        {
                            text: __("TT"),
                            dataIndex: "create_tt",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Wait Condition"),
                            dataIndex: "wait_condition",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Stop"),
                            dataIndex: "stop_processing",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        }
                     ]
                },
                {
                    name: "telemetry_sample",
                    xtype: "numberfield",
                    fieldLabel: __("Tememetry Sample"),
                    allowBlank: false,
                    min: 0,
                    uiStyle: "small"
                }
            ],
        });
        me.callParent();
    }
});
