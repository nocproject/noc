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
        "NOC.core.tagfield.Tagfield",
        "NOC.fm.alarmclass.LookupField",
        "NOC.fm.alarmseverity.LookupField",
        "NOC.fm.escalationprofile.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.notificationgroup.LookupField",
        "NOC.main.handler.LookupField",
        "NOC.sa.action.LookupField",
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
                    name: 'description',
                    xtype: 'textarea',
                    fieldLabel: __('Description'),
                    uiStyle: 'large'
                },
                {
                    name: "severity_policy",
                    xtype: "combobox",
                    fieldLabel: __("Severity Policy"),
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
                    name: "min_severity",
                    xtype: "fm.alarmseverity.LookupField",
                    fieldLabel: __("Min./Set Severity"),
                    uiStyle: "medium",
                    allowBlank: true
                },
                {
                    name: "min_severity",
                    xtype: "fm.alarmseverity.LookupField",
                    fieldLabel: __("Min./Set Severity"),
                    uiStyle: "medium",
                    allowBlank: true
                },
                {
                    name: "escalation_profile",
                    xtype: "fm.escalationprofile.LookupField",
                    fieldLabel: __("Escalation Profile"),
                    uiStyle: "medium",
                    allowBlank: true
                },
                {
                  name: "rule_action",
                  xtype: "combobox",
                  fieldLabel: __("Rule Action"),
                  store: [
                    ["continue", __("Continue")],
                    ["drop", __("Drop Alarm")],
                    ["rewrite", __("Rewrite")]
                  ],
                  value: "continue",
                  uiStyle: "medium",
                },
                {
                    name: "alarm_class",
                    xtype: "fm.alarmclass.LookupField",
                    fieldLabel: __("Alarm Class"),
                    uiStyle: "large",
                    allowBlank: true
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
                            text: __("When Do"),
                            dataIndex: "when",
                            width: 100,
                            allowBlank: false,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["raise", __("On Alarm Raise")],
                                    ["update", __("On Update")],
                                    ["clear", __("On Alarm Clear")],
                                ]
                            },
                            renderer: NOC.render.Choices({
                                "raise": __("On Alarm Raise"),
                                "clear": __("On Alarm Clear"),
                            })
                        },
                        {
                            text: __("Notification Group"),
                            dataIndex: "notification_group",
                            editor: "main.notificationgroup.LookupField",
                            width: 150,
                            allowBlank: true,
                            renderer: NOC.render.Lookup("notification_group")
                        },
                        {
                            text: __("Template"),
                            dataIndex: "template",
                            editor: "main.template.LookupField",
                            width: 150,
                            allowBlank: true,
                            renderer: NOC.render.Lookup("template")
                        },
                        {
                            text: __("Object Action"),
                            dataIndex: "object_action",
                            editor: "sa.action.LookupField",
                            width: 150,
                            allowBlank: true,
                            renderer: NOC.render.Lookup("object_action")
                        },
                        {
                            text: __("Message"),
                            dataIndex: "message",
                            editor: "textfield",
                            allowBlank: true,
                            width: 200
                        },
                        {
                            text: __("Handler"),
                            dataIndex: "handler",
                            editor: {
                                xtype: "main.handler.LookupField",
                                query: {
                                    "allow_fm_alarmgroup": true
                                }
                            },
                            renderer: NOC.render.Lookup("handler"),
                            width: 200
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
                            xtype: "core.tagfield",
                            url: "/inv/resourcegroup/lookup/",
                            fieldLabel: __("Object Groups"),
                            name: "resource_groups",
                            allowBlank: true,
                            uiStyle: "extra"
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
