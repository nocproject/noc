//---------------------------------------------------------------------
// fm.alarmrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmrule.Application");

Ext.define("NOC.fm.alarmrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.alarmrule.Model",
        "NOC.core.label.LabelField",
        "NOC.core.ListFormField",
        "NOC.fm.alarmclass.LookupField",
        "NOC.fm.alarmseverity.LookupField",
        "NOC.fm.ttsystem.LookupField",
        "NOC.main.notificationgroup.LookupField",
        "NOC.main.handler.LookupField",
        "NOC.fm.escalationprofile.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.timepattern.LookupField",
        "NOC.aaa.user.LookupField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.fm.alarmrule.Model",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 300,
                    align: "left"
                },
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    renderer: NOC.render.Bool,
                    width: 100,
                    align: "left"
                },
                {
                    text: __("Escalation Profile"),
                    dataIndex: "escalation_profile",
                    width: 200,
                    renderer: NOC.render.Lookup("escalation_profile")
                }
            ],

            fields: [
                {
                    name: 'name',
                    xtype: 'textfield',
                    fieldLabel: __('Name'),
                    allowBlank: false,
                    uiStyle: 'large'
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    uiStyle: "large"
                },
                {
                    name: "severity_policy",
                    xtype: "combobox",
                    fieldLabel: __("Calc Severity Policy"),
                    allowBlank: true,
                    store: [
                        ["CB", __("Class Based Policy")],
                        ["AB", __("Affected Based Severity Preferred")],
                        ["AL", __("Affected Limit")],
                        ["ST", __("By Tokens")]
                    ],
                    uiStyle: "medium",
                    value: "AL",
                },
                {
                    name: "escalation_profile",
                    xtype: "fm.escalationprofile.LookupField",
                    fieldLabel: __("Escalation Profile"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "rule_action",
                    xtype: "combobox",
                    fieldLabel: __("Action"),
                    allowBlank: true,
                    store: [
                        ["continue", __("Continue processed")],
                        ["drop", __("Drop Alarm")],
                        ["rewrite", __("Rewrite Alarm Class")]
                    ],
                    uiStyle: "medium",
                    value: "continue",
                },
                {
                    name: "groups",
                    xtype: "gridfield",
                    fieldLabel: __("Group Alarm"),
                    columns: [
                        {
                            text: __("Minimum alarms"),
                            dataIndex: "min_threshold",
                            editor: {
                                xtype: "numberfield"
                            },
                            minValue: 0,
                            defaultValue: 0,
                            width: 50
                        },
                        {
                            text: __("Maximum alarms"),
                            dataIndex: "max_threshold",
                            editor: {
                                xtype: "numberfield"
                            },
                            minValue: 0,
                            defaultValue: 1,
                            width: 50
                        },
                        {
                            text: __("Window (sec.)"),
                            dataIndex: "window",
                            editor: {
                                xtype: "numberfield"
                            },
                            minValue: 0,
                            defaultValue: 0,
                            width: 50
                        },
                        {
                            text: __("Reference Template"),
                            dataIndex: "reference_template",
                            editor: "textfield",
                            width: 250
                        },
                        {
                            text: __("Alarm Class"),
                            dataIndex: "alarm_class",
                            editor: "fm.alarmclass.LookupField",
                            renderer: NOC.render.Lookup("alarm_class"),
                            width: 200
                        },
                        {
                            text: __("Title Template"),
                            dataIndex: "title_template",
                            editor: "textfield",
                            allowBlank: true,
                            width: 200
                        },
                        {
                            text: __("Labels"),
                            dataIndex: "labels",
                            renderer: NOC.render.LabelField,
                            allowBlank: true,
                            editor: {
                                xtype: "labelfield",
                                query: {
                                    "allow_models": ["fm.Alarm"]
                                }},
                            width: 200
                        }
                    ]
                },
                {
                    name: "actions",
                    xtype: "gridfield",
                    fieldLabel: __("Actions"),
                    columns: [
                        {
                            text: __("Delay"),
                            dataIndex: "delay",
                            editor: "numberfield",
                            width: 75
                        },
                        {
                            text: __("When Do"),
                            dataIndex: "when",
                            width: 100,
                            allowBlank: false,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["raise", __("On Alarm Raise")],
                                    ["clear", __("On Alarm Clear")],
                                ]
                            },
                            renderer: NOC.render.Choices({
                                "raise": __("On Alarm Raise"),
                                "clear": __("On Alarm Clear"),
                            })
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
                            text: __("Action"),
                            dataIndex: "action",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["create_tt", __("Create TT")],
                                    ["notify", __("Notification")],
                                    ["log", __("Add Log")],
                                    ["ack", __("Acknowledge")],
                                    ["handler", __("Handler")],
                                    ["subscribe", __("Subscribe")],
                                    // ["clear", __("Clear Alarm")],
                                ]
                            },
                            renderer: NOC.render.Choices({
                                "ack": __("Acknowledge"),
                                "nack": __("Not Acknowledge"),
                                "any": __("Any")
                            })
                        },
                        {
                            text: __("TT System"),
                            dataIndex: "tt_system",
                            editor: "fm.ttsystem.LookupField",
                            width: 120,
                            renderer: NOC.render.Lookup("tt_system")
                        },
                        {
                            text: __("Notification Group"),
                            dataIndex: "notification_group",
                            editor: "main.notificationgroup.LookupField",
                            width: 150,
                            renderer: NOC.render.Lookup("notification_group")
                        },
                        {
                            text: __("Template"),
                            dataIndex: "template",
                            editor: "main.template.LookupField",
                            width: 150,
                            renderer: NOC.render.Lookup("template")
                        },
                        {
                            text: __("User"),
                            dataIndex: "user",
                            editor: "aaa.user.LookupField",
                            width: 100,
                            renderer: NOC.render.Lookup("user")
                        },
                        // {
                        //     text: __("Max. Repeats"),
                        //     dataIndex: "max_repeats",
                        //     editor: "numberfield",
                        //     width: 75
                        // },
                        {
                            text: __("Allow Fail"),
                            dataIndex: "allow_fail",
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
                    name: "match",
                    xtype: "listform",
                    fieldLabel: __("Match Rules"),
                    rows: 5,
                    items: [
                        {
                            name: "labels",
                            xtype: "labelfield",
                            fieldLabel: __("Match Labels"),
                            allowBlank: true,
                            isTree: true,
                            filterProtected: false,
                            pickerPosition: "down",
                            uiStyle: "extra",
                            query: {
                                "allow_matched": true
                            }
                        },
                        {
                            name: "exclude_labels",
                            xtype: "labelfield",
                            fieldLabel: __("Exclude Match Labels"),
                            allowBlank: true,
                            isTree: true,
                            filterProtected: false,
                            pickerPosition: "down",
                            uiStyle: "extra",
                            query: {
                                "allow_matched": true
                            }
                        },
                        {
                            name: "alarm_class",
                            xtype: "fm.alarmclass.LookupField",
                            fieldLabel: __("Alarm Class"),
                            uiStyle: 'large',
                            allowBlank: true
                        },
                        {
                            name: "severity",
                            xtype: "fm.alarmseverity.LookupField",
                            fieldLabel: __("Alarm Severity"),
                            uiStyle: 'medium',
                            allowBlank: true
                        },
                        {
                            name: 'reference_rx',
                            xtype: 'textfield',
                            fieldLabel: __('Group Reference Regex'),
                            uiStyle: 'large',
                            allowBlank: true
                        },
                    ]
                }
            ]
        });
        me.callParent();
    }
});
