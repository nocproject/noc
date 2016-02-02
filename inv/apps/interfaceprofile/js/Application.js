//---------------------------------------------------------------------
// inv.interfaceprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interfaceprofile.Application");

Ext.define("NOC.inv.interfaceprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.interfaceprofile.Model",
        "NOC.main.style.LookupField",
        "NOC.main.notificationgroup.LookupField",
        "Ext.ux.form.MultiIntervalField",
        "NOC.pm.metrictype.LookupField"
    ],
    model: "NOC.inv.interfaceprofile.Model",
    search: true,
    rowClassField: "row_class",
    validationModelId: "inv.InterfaceProfile",

    initComponent: function () {
        var me = this;

        me.ITEM_VALIDATION_SETTINGS = me.registerItem(
            Ext.create("NOC.cm.validationpolicysettings.ValidationSettingsPanel", {
                app: me,
                validationModelId: me.validationModelId
            })
        );

        me.validationSettingsButton = Ext.create("Ext.button.Button", {
            text: "Validation",
            glyph: NOC.glyph.file,
            scope: me,
            handler: me.onValidationSettings
        });

        Ext.apply(me, {
                columns: [
                    {
                        text: "Name",
                        dataIndex: "name"
                    },
                    {
                        text: "Link Events",
                        dataIndex: "link_events",
                        renderer: function (value) {
                            return {
                                "I": "Ignore",
                                "L": "Log",
                                "A": "Raise"
                            }[value];
                        }
                    },
                    {
                        text: "Style",
                        dataIndex: "style",
                        renderer: NOC.render.Lookup("style")
                    },
                    {
                        text: "Policy",
                        dataIndex: "discovery_policy",
                        renderer: NOC.render.Choices({
                            I: "Ignore",
                            O: "Create new",
                            R: "Replace",
                            C: "Cloud"
                        })
                    },
                    {
                        text: "MAC",
                        dataIndex: "mac_discovery",
                        renderer: NOC.render.Bool,
                        width: 50
                    },
                    {
                        text: "Description",
                        dataIndex: "description",
                        flex: 1
                    }
                ],
                fields: [
                    {
                        name: "name",
                        xtype: "textfield",
                        fieldLabel: "Name",
                        allowBlank: false
                    },
                    {
                        name: "description",
                        xtype: "textarea",
                        fieldLabel: "Description",
                        allowBlank: true
                    },
                    {
                        name: "style",
                        xtype: "main.style.LookupField",
                        fieldLabel: "Style",
                        allowBlank: true
                    },
                    {
                        name: "link_events",
                        xtype: "combobox",
                        fieldLabel: "Link Events",
                        allowBlank: false,
                        queryMode: "local",
                        displayField: "label",
                        valueField: "id",
                        store: {
                            fields: ["id", "label"],
                            data: [
                                {id: "I", label: "Ignore Link Events"},
                                {
                                    id: "L",
                                    label: "Log events, do not raise alarms"
                                },
                                {id: "A", label: "Raise alarms"}
                            ]
                        },
                        uiStyle: "medium"
                    },
                    {
                        name: "discovery_policy",
                        xtype: "combobox",
                        fieldLabel: "Discovery Policy",
                        allowBlank: false,
                        queryMode: "local",
                        displayField: "label",
                        valueField: "id",
                        store: {
                            fields: ["id", "label"],
                            data: [
                                {id: "I", label: "Ignore"},
                                {id: "O", label: "Create new"},
                                {id: "R", label: "Replace"},
                                {id: "C", label: "Cloud"}
                            ]
                        },
                        uiStyle: "medium"
                    },
                    {
                        name: "check_link_interval",
                        xtype: "multiintervalfield",
                        fieldLabel: "check_link interval",
                        allowBlank: true
                    },
                    {
                        name: "mac_discovery",
                        xtype: "checkbox",
                        boxLabel: "MAC Discovery",
                        allowBlank: true
                    },
                    {
                        name: "status_change_notification",
                        xtype: "main.notificationgroup.LookupField",
                        fieldLabel: "Status Change Notification",
                        allowBlank: true
                    },
                    {
                        name: "is_customer",
                        xtype: "checkbox",
                        boxLabel: "Customer port",
                        allowBlank: true
                    },
                    {
                        name: "metrics",
                        xtype: "gridfield",
                        fieldLabel: "Metrics",
                        columns: [
                            {
                                text: "Metric Type",
                                dataIndex: "metric_type",
                                width: 150,
                                editor: "pm.metrictype.LookupField",
                                renderer: NOC.render.Lookup("metric_type")
                            },
                            {
                                text: "Active",
                                dataIndex: "is_active",
                                width: 50,
                                renderer: NOC.render.Bool,
                                editor: "checkbox"
                            },
                            {
                                text: "Low Error",
                                dataIndex: "low_error",
                                width: 60,
                                editor: "textfield",
                                align: "right"
                            },
                            {
                                text: "Low Warn",
                                dataIndex: "low_warn",
                                width: 60,
                                editor: "textfield",
                                align: "right"
                            },
                            {
                                text: "High Warn",
                                dataIndex: "high_warn",
                                width: 60,
                                editor: "textfield",
                                align: "right"
                            },
                            {
                                text: "High Error",
                                dataIndex: "high_error",
                                width: 60,
                                editor: "textfield",
                                align: "right"
                            }
                        ]

                    }
                ],
                formToolbar: [
                    me.validationSettingsButton
                ]

            }
        );
        me.callParent();
    },
    //
    onValidationSettings: function () {
        var me = this;
        me.showItem(me.ITEM_VALIDATION_SETTINGS).preview(me.currentRecord);
    }
});
