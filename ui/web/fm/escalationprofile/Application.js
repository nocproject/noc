//---------------------------------------------------------------------
// fm.escalationprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.escalationprofile.Application");

Ext.define("NOC.fm.escalationprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.escalationprofile.Model",
        "NOC.fm.ttsystem.LookupField",
        "NOC.fm.alarmseverity.LookupField",
        "NOC.main.template.LookupField",
        "NOC.aaa.user.LookupField",
        "NOC.aaa.group.LookupField",
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
                    allowBlank: true,
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
                    allowBlank: true,
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
                    name: "repeat_escalations",
                    xtype: "combobox",
                    fieldLabel: __("Repeat Escalations"),
                    allowBlank: false,
                    queryMode: "local",
                    displayField: "label",
                    valueField: "id",
                    store: {
                        fields: ["id", "label"],
                        data: [
                            {id: "N", label: "Newer"},
                            {id: "S", label: "Severity Change"},
                            {id: "D", label: "After delay"}]
                    },
                    uiStyle: "medium"
                },
                {
                    name: "tt_system_config",
                    xtype: "gridfield",
                    fieldLabel: __("TT System Config"),
                    columns: [
                        {
                            text: __("TT System"),
                            dataIndex: "tt_system",
                            editor: "fm.ttsystem.LookupField",
                            renderer: NOC.render.Lookup("tt_system"),
                            width: 150
                        },
                        {
                            text: __("Pre Reason"),
                            dataIndex: "pre_reason",
                            editor: "textfield",
                            width: 150
                        },
                        {
                            text: __("Login"),
                            dataIndex: "login",
                            editor: "textfield",
                            width: 150
                        }
                    ]
                },
                {
                    name: "actions",
                    xtype: "gridfield",
                    fieldLabel: __("Actions"),
                    columns: [
                        {
                            text: __("User"),
                            dataIndex: "user",
                            editor: "aaa.user.LookupField",
                            renderer: NOC.render.Lookup("user"),
                            width: 150
                        },
                        {
                            text: __("Group"),
                            dataIndex: "group",
                            editor: "aaa.group.LookupField",
                            renderer: NOC.render.Lookup("group"),
                            width: 150
                        },
                        {
                            text: __("Ack"),
                            dataIndex: "ack",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Add log"),
                            dataIndex: "log",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Close"),
                            dataIndex: "close",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Subscribe"),
                            dataIndex: "subscribe",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        }
                    ]
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
                            text: __("Match Ack"),
                            dataIndex: "alarm_ack",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["ack", __("Acknowledge")],
                                    ["nack", __("Not Acknowledge")],
                                    ["any", __("Any")]
                                ]
                            },
                            renderer: NOC.render.Choices({
                                "ack": __("Acknowledge"),
                                "nack": __("Not Acknowledge"),
                                "any": __("Any")
                            })
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
                            editor: "fm.alarmseverity.LookupField",
                            width: 120,
                            renderer: NOC.render.Lookup("min_severity")
                        },
                        {
                            text: __("TT System"),
                            dataIndex: "tt_system",
                            editor: "fm.ttsystem.LookupField",
                            width: 120,
                            renderer: NOC.render.Lookup("tt_system")
                        },
                        {
                            text: __("TT Queue"),
                            dataIndex: "tt_queue",
                            editor: "textfield",
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
                            width: 150,
                            renderer: NOC.render.Lookup("template")
                        },
                        {
                            text: __("Close Template"),
                            dataIndex: "close_template",
                            editor: "main.template.LookupField",
                            width: 150,
                            renderer: NOC.render.Lookup("close_template")
                        },
                        {
                            text: __("TT"),
                            dataIndex: "create_tt",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Register Msg."),
                            dataIndex: "register_message",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Acl Policy"),
                            dataIndex: "ack_policy",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["D", __("Disabled")],
                                    ["U", __("UnAck")],
                                    ["A", __("Ack User")],
                                    ["S", __("Ack Subscriber")]
                                ]
                            },
                            renderer: NOC.render.Choices({
                                "D": __("Disabled"),
                                "U": __("UnAck"),
                                "A": __("Ack User"),
                                "S": __("Ack Subscriber")
                            })
                        },
                        {
                            text: __("Assigned User"),
                            dataIndex: "assigned_user",
                            editor: "aaa.user.LookupField",
                            renderer: NOC.render.Lookup("assigned_user"),
                            width: 150
                        },
                        {
                            text: __("Repeat"),
                            dataIndex: "repeat",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Max. Repeats"),
                            dataIndex: "max_repeats",
                            editor: "numberfield",
                            width: 75
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
                    name: "repeat_delay",
                    xtype: "numberfield",
                    fieldLabel: __("Repeat Delay"),
                    allowBlank: true,
                    min: 30,
                    uiStyle: "small"
                },
                {
                    name: "telemetry_sample",
                    xtype: "numberfield",
                    fieldLabel: __("Tememetry Sample"),
                    allowBlank: true,
                    min: 0,
                    uiStyle: "small"
                }
            ],
        });
        me.callParent();
    }
});
