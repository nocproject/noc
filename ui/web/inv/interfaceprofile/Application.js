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
        "NOC.pm.metrictype.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.main.ref.windowfunction.LookupField",
        "NOC.pm.thresholdprofile.LookupField"
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
                        dataIndex: "mac_discovery_policy",
                        renderer: NOC.render.Choices({
                            e: __("Enable"),
                            d: __("Disable"),
                            m: __("Management VLAN")
                        }),
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
                        name: "mac_discovery_policy",
                        xtype: "combobox",
                        fieldLabel: __("MAC Discovery Policy"),
                        allowBlank: false,
                        store: [
                            ["e", __("Enable")],
                            ["d", __("Disable")],
                            ["m", __("Management VLAN")]
                        ],
                        uiStyle: "medium"
                    },
                    {
                        name: "allow_lag_mismatch",
                        xtype: "checkbox",
                        boxLabel: __("Allow LAG mismatch"),
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
                        name: "is_uni",
                        xtype: "checkbox",
                        boxLabel: __("User Interface"),
                        allowBlank: true
                    },
                    {
                        name: "allow_autosegmentation",
                        xtype: "checkbox",
                        boxLabel: __("Allow Autosegmentation"),
                        allowBlank: true
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
                        name: "allow_subinterface_metrics",
                        xtype: "checkbox",
                        boxLabel: __("Apply metrics to subinterfaces"),
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
                                editor: {
                                    xtype: "pm.metrictype.LookupField"
                                },
                                renderer: NOC.render.Lookup("metric_type")
                            },
                            {
                                text: __("Box"),
                                dataIndex: "enable_box",
                                width: 50,
                                renderer: NOC.render.Bool,
                                editor: "checkbox"
                            },
                            {
                                text: __("Periodic"),
                                dataIndex: "enable_periodic",
                                width: 50,
                                renderer: NOC.render.Bool,
                                editor: "checkbox"
                            },
                            {
                                text: __("Stored"),
                                dataIndex: "is_stored",
                                width: 50,
                                renderer: NOC.render.Bool,
                                editor: "checkbox"
                            },
                            {
                                text: __("Window"),
                                dataIndex: "window",
                                width: 50,
                                editor: "textfield"
                            },
                            {
                                text: __("Window Type"),
                                dataIndex: "window_type",
                                width: 70,
                                renderer: NOC.render.Choices({
                                    m: __("Measurements"),
                                    t: __("Seconds")
                                }),
                                editor: {
                                    xtype: "combobox",
                                    store: [
                                        ["m", __("Measurements")],
                                        ["t", __("Seconds")]
                                    ]
                                }
                            },
                            {
                                text: __("Window Function"),
                                dataIndex: "window_function",
                                width: 70,
                                editor: {
                                    xtype: "main.ref.windowfunction.LookupField"
                                }
                            },
                            {
                                text: __("Config"),
                                dataIndex: "window_config",
                                width: 70,
                                editor: "textfield"
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
                            },
                            {
                                text: __("Profile"),
                                dataIndex: "threshold_profile",
                                width: 150,
                                editor: {
                                    xtype: "pm.thresholdprofile.LookupField"
                                },
                                renderer: NOC.render.Lookup("threshold_profile")
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
