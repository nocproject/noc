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
        "NOC.main.notificationgroup.LookupField",
        "NOC.main.handler.LookupField",
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
                    width: 100,
                    align: "left"
                },
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    renderer: NOC.render.Bool,
                    width: 100,
                    align: "left"
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
                    name: "groups",
                    xtype: "gridfield",
                    fieldLabel: __("Group Alarm"),
                    columns: [
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
                            width: 250
                        },
                        {
                            text: __("Title Template"),
                            dataIndex: "title_template",
                            editor: "textfield",
                            allowBlank: true,
                            flex: 1
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
                                    ["clear", __("On Alarm Clear")],
                                ]
                            },
                            renderer: NOC.render.Choices({
                                "raise": __("On Alarm Raise"),
                                "clear": __("On Alarm Clear"),
                            })
                        },
                        {
                            text: __("Action Policy"),
                            dataIndex: "policy",
                            width: 100,
                            allowBlank: false,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["continue", __("Continue Processed")],
                                    ["drop", __("Drop Alarm")],
                                    ["rewrite", __("Rewrite AlarmClass")]
                                ]
                            },
                            value: "continue",
                            renderer: NOC.render.Choices({
                                "continue": __("Continue Processed"),
                                "drop": __("Drop Alarm"),
                                "rewrite": __("Rewrite AlarmClass")
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
                        },
                        {
                            text: __("Alarm Class"),
                            dataIndex: "alarm_class",
                            editor: "fm.alarmclass.LookupField",
                            allowBlank: true,
                            renderer: NOC.render.Lookup("alarm_class"),
                            width: 250
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
