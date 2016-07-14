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
            text: __("Validation"),
            glyph: NOC.glyph.file,
            scope: me,
            handler: me.onValidationSettings
        });

        Ext.apply(me, {
                columns: [
                    {
                        text: __("Name"),
                        dataIndex: "name"
                    },
                    {
                        text: __("Link Events"),
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
                        text: __("Style"),
                        dataIndex: "style",
                        renderer: NOC.render.Lookup("style")
                    },
                    {
                        text: __("Policy"),
                        dataIndex: "discovery_policy",
                        renderer: NOC.render.Choices({
                            I: "Ignore",
                            O: "Create new",
                            R: "Replace",
                            C: "Cloud"
                        })
                    },
                    {
                        text: __("MAC"),
                        dataIndex: "mac_discovery",
                        renderer: NOC.render.Bool,
                        width: 50
                    },
                    {
                        text: __("Description"),
                        dataIndex: "description",
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
                        name: "style",
                        xtype: "main.style.LookupField",
                        fieldLabel: __("Style"),
                        allowBlank: true
                    },
                    {
                        name: "link_events",
                        xtype: "combobox",
                        fieldLabel: __("Link Events"),
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
                        fieldLabel: __("Discovery Policy"),
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
                        name: "weight",
                        xtype: "numberfield",
                        fieldLabel: __("Alarm Weight"),
                        allowBlank: false,
                        uiStyle: "small"
                    },
                    {
                        name: "mac_discovery",
                        xtype: "checkbox",
                        boxLabel: __("MAC Discovery"),
                        allowBlank: true
                    },
                    {
                        name: "status_discovery",
                        xtype: "checkbox",
                        boxLabel: __("Status Discovery"),
                        allowBlank: true
                    },
                    {
                        name: "status_change_notification",
                        xtype: "main.notificationgroup.LookupField",
                        fieldLabel: __("Status Change Notification"),
                        allowBlank: true
                    },
                    {
                        name: "metrics",
                        xtype: "gridfield",
                        fieldLabel: __("Metrics"),
                        columns: [
                            {
                                text: __("Metric Type"),
                                dataIndex: "metric_type",
                                width: 150,
                                editor: "pm.metrictype.LookupField",
                                renderer: NOC.render.Lookup("metric_type")
                            },
                            {
                                text: __("Active"),
                                dataIndex: "is_active",
                                width: 50,
                                renderer: NOC.render.Bool,
                                editor: "checkbox"
                            },
                            {
                                text: __("Low Error"),
                                dataIndex: "low_error",
                                width: 60,
                                editor: "textfield",
                                align: "right",
                                renderer: NOC.render.Size
                            },
                            {
                                text: __("Low Warn"),
                                dataIndex: "low_warn",
                                width: 60,
                                editor: "textfield",
                                align: "right",
                                renderer: NOC.render.Size
                            },
                            {
                                text: __("High Warn"),
                                dataIndex: "high_warn",
                                width: 60,
                                editor: "textfield",
                                align: "right",
                                renderer: NOC.render.Size
                            },
                            {
                                text: __("High Error"),
                                dataIndex: "high_error",
                                width: 60,
                                editor: "textfield",
                                align: "right",
                                renderer: NOC.render.Size
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
    },
    //
    cleanData: function(v) {
        Ext.each(v.metrics, function(m) {
            if(m.low_error === "") {
                m.low_error = null;
            }
            if(m.low_warn === "") {
                m.low_warn = null;
            }
            if(m.high_warn === "") {
                m.high_warn = null;
            }
            if(m.high_error === "") {
                m.high_error = null;
            }
        });
    }
});
