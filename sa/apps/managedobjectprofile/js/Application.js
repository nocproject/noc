//---------------------------------------------------------------------
// sa.managedobjectprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectprofile.Application");

Ext.define("NOC.sa.managedobjectprofile.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.sa.managedobjectprofile.Model",
        "NOC.main.style.LookupField",
        "NOC.main.ref.stencil.LookupField",
        "Ext.ux.form.MultiIntervalField",
        "NOC.pm.metrictype.LookupField"
    ],
    model: "NOC.sa.managedobjectprofile.Model",
    search: true,
    rowClassField: "row_class",
    validationModelId: "sa.ManagedObjectProfile",

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
                    text: "Level",
                    dataIndex: "level",
                    width: 60,
                    align: "right"
                },
                {
                    text: "Ping",
                    dataIndex: "enable_ping",
                    width: 100,
                    renderer: function(value, meta, record) {
                        var v = NOC.render.Bool(value);
                        if(value) {
                            v += " " + NOC.render.Duration(record.get("ping_interval"));
                            if(record.get("report_ping_rtt")) {
                                v += "+RTT"
                            }
                        }
                        return v
                    },
                    align: "center"
                },
                {
                    text: "Sync IPAM",
                    dataIndex: "sync_ipam",
                    width: 60,
                    renderer: NOC.render.Bool,
                    align: "center"
                },
                {
                    text: "Box discovery",
                    dataIndex: "enable_box_discovery",
                    width: 100,
                    renderer: function(value, meta, record) {
                        var v = NOC.render.Bool(value);
                        if(value) {
                            v += " " + NOC.render.Duration(record.get("box_discovery_interval"));
                        }
                        return v
                    },
                    align: "center"
                },
                {
                    text: "Failed interval",
                    dataIndex: "box_discovery_failed_interval",
                    width: 100,
                    renderer: NOC.render.Duration,
                    align: "center"
                },
                {
                    text: "Periodic discovery",
                    dataIndex: "enable_periodic_discovery",
                    width: 100,
                    renderer: function(value, meta, record) {
                        var v = NOC.render.Bool(value);
                        if(value) {
                            v += " " + NOC.render.Duration(record.get("periodic_discovery_interval"));
                        }
                        return v
                    },
                    align: "center"
                },
                {
                    text: "Objects",
                    dataIndex: "mo_count",
                    width: 60,
                    align: "right",
                    sortable: false
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
                    xtype: "tabpanel",
                    layout: "fit",
                    autoScroll: true,
                    anchor: "-0, -50",
                    defaults: {
                        autoScroll: true,
                        layout: "anchor",
                        padding: 10
                    },
                    items: [
                        {
                            title: "Common",
                            items: [
                                {
                                    name: "description",
                                    xtype: "textarea",
                                    fieldLabel: "Description",
                                    allowBlank: true,
                                    uiStyle: "extra"
                                },
                                {
                                    name: "level",
                                    xtype: "numberfield",
                                    fieldLabel: "Level",
                                    allowBlank: false,
                                    uiStyle: "small"
                                },
                                {
                                    name: "style",
                                    xtype: "main.style.LookupField",
                                    fieldLabel: "Style",
                                    allowBlank: true
                                },
                                {
                                    name: "shape",
                                    xtype: "main.ref.stencil.LookupField",
                                    fieldLabel: "Shape",
                                    allowBlank: true
                                },
                                {
                                    name: "name_template",
                                    xtype: "textfield",
                                    fieldLabel: "Name template",
                                    allowBlank: true,
                                    uiStyle: "large"
                                }
                            ]
                        },
                        {
                            title: "Card",
                            items: [
                                {
                                    name: "card",
                                    xtype: "textfield",
                                    fieldLabel: "Card",
                                    allowBlank: true,
                                    uiStyle: "extra"
                                },
                                {
                                    name: "card_title_template",
                                    xtype: "textfield",
                                    fieldLabel: "Card Title Template",
                                    allowBlank: false,
                                    uiStyle: "extra"
                                }
                            ]
                        },
                        {
                            title: "IPAM",
                            items: [
                                {
                                    name: "sync_ipam",
                                    xtype: "checkboxfield",
                                    boxLabel: "Enable IPAM synchronization",
                                    allowBlank: false
                                },
                                {
                                    name: "fqdn_template",
                                    xtype: "textarea",
                                    fieldLabel: "FQDN template",
                                    allowBlank: true,
                                    uiStyle: "extra"
                                }
                            ]
                        },
                        {
                            title: "Ping Check",
                            items: [
                                {
                                    name: "enable_ping",
                                    xtype: "checkboxfield",
                                    boxLabel: "Enable",
                                    allowBlank: false

                                },
                                {
                                    xtype: "fieldset",
                                    title: "Ping discovery intervals",
                                    layout: "vbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "ping_interval",
                                                    xtype: "numberfield",
                                                    fieldLabel: "Interval, sec",
                                                    uiStyle: "small",
                                                    listeners: {
                                                        scope: me,
                                                        change: function(_item, newValue, oldValue, eOpts) {
                                                            me.form.findField("ping_calculated").setValue(newValue);
                                                        }
                                                    }
                                                },
                                                {
                                                    name: 'ping_calculated',
                                                    xtype: 'displayfield',
                                                    renderer: NOC.render.Duration
                                                }
                                            ]
                                        },
                                    ]
                                },
                                {
                                    name: "report_ping_rtt",
                                    xtype: "checkboxfield",
                                    boxLabel: "Report ping RTT",
                                    allowBlank: false
                                }
                            ]
                        },
                        {
                            title: "FM",
                            items: [
                                {
                                    name: "weight",
                                    xtype: "numberfield",
                                    fieldLabel: "Alarm Weight",
                                    allowBlank: false,
                                    uiStyle: "small"
                                }
                            ]
                        },
                        {
                            title: "Box discovery",
                            items: [
                                {
                                    name: "enable_box_discovery",
                                    xtype: "checkbox",
                                    boxLabel: "Enable"
                                },
                                {
                                    xtype: "fieldset",
                                    title: "Box discovery intervals",
                                    layout: "vbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "box_discovery_interval",
                                                    xtype: "numberfield",
                                                    fieldLabel: "Interval, sec",
                                                    labelWidth: 150,
                                                    allowBlank: false,
                                                    uiStyle: "medium",
                                                    listeners: {
                                                        scope: me,
                                                        change: function(_item, newValue, oldValue, eOpts) {
                                                            me.form.findField("box_discovery_interval_calculated").setValue(newValue);
                                                        }
                                                    }
                                                },
                                                {
                                                    name: 'box_discovery_interval_calculated',
                                                    xtype: 'displayfield',
                                                    renderer: NOC.render.Duration
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "box_discovery_failed_interval",
                                                    xtype: "numberfield",
                                                    fieldLabel: "Failed Interval, sec",
                                                    labelWidth: 150,
                                                    allowBlank: false,
                                                    uiStyle: "medium",
                                                    listeners: {
                                                        scope: me,
                                                        change: function(_item, newValue, oldValue, eOpts) {
                                                            me.form.findField("box_discovery_failed_interval_calculated").setValue(newValue);
                                                        }
                                                    }
                                                },
                                                {
                                                    name: 'box_discovery_failed_interval_calculated',
                                                    xtype: 'displayfield',
                                                    renderer: NOC.render.Duration
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "4 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "box_discovery_on_system_start",
                                                    xtype: "checkbox",
                                                    boxLabel: "Check on system start after "
                                                },
                                                {
                                                    name: "box_discovery_system_start_delay",
                                                    xtype: "numberfield",
                                                    allowBlank: false,
                                                    labelWidth: 10,
                                                    uiStyle: "small"
                                                },
                                                {
                                                    name: "_box_discovery_system_start_delay",
                                                    xtype: 'displayfield',
                                                    value: "sec"
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "4 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "box_discovery_on_config_changed",
                                                    xtype: "checkbox",
                                                    boxLabel: "Check on config change after "
                                                },
                                                {
                                                    name: "box_discovery_config_changed_delay",
                                                    xtype: "numberfield",
                                                    allowBlank: false,
                                                    labelWidth: 10,
                                                    uiStyle: "small"
                                                },
                                                {
                                                    name: "_box_discovery_config_changed_delay",
                                                    xtype: 'displayfield',
                                                    value: "sec"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    xtype: "container",
                                    layout: {
                                        type: "table",
                                        columns: 4
                                    },
                                    defaults: {
                                        padding: "4 8 0 0"
                                    },
                                    items: [
                                        {
                                            name: "enable_box_discovery_profile",
                                            xtype: "checkboxfield",
                                            boxLabel: "Profile"
                                        },
                                        {
                                            name: "enable_box_discovery_version",
                                            xtype: "checkboxfield",
                                            boxLabel: "Version"
                                        },
                                        {
                                            name: "enable_box_discovery_caps",
                                            xtype: "checkboxfield",
                                            boxLabel: "Caps"
                                        },
                                        {
                                            name: "enable_box_discovery_interface",
                                            xtype: "checkboxfield",
                                            boxLabel: "Interface"
                                        },
                                        {
                                            name: "enable_box_discovery_prefix",
                                            xtype: "checkboxfield",
                                            boxLabel: "Prefix"
                                        },
                                        {
                                            name: "enable_box_discovery_id",
                                            xtype: "checkboxfield",
                                            boxLabel: "ID"
                                        },
                                        {
                                            name: "enable_box_discovery_config",
                                            xtype: "checkboxfield",
                                            boxLabel: "Config"
                                        },
                                        {
                                            name: "enable_box_discovery_asset",
                                            xtype: "checkboxfield",
                                            boxLabel: "Asset"
                                        },
                                        {
                                            name: "enable_box_discovery_vlan",
                                            xtype: "checkboxfield",
                                            boxLabel: "VLAN"
                                        },
                                        {
                                            name: "enable_box_discovery_nri",
                                            xtype: "checkboxfield",
                                            boxLabel: "NRI"
                                        },
                                        {
                                            name: "enable_box_discovery_bfd",
                                            xtype: "checkboxfield",
                                            boxLabel: "BFD"
                                        },
                                        {
                                            name: "enable_box_discovery_cdp",
                                            xtype: "checkboxfield",
                                            boxLabel: "CDP"
                                        },
                                        {
                                            name: "enable_box_discovery_fdp",
                                            xtype: "checkboxfield",
                                            boxLabel: "FDP"
                                        },
                                        {
                                            name: "enable_box_discovery_lldp",
                                            xtype: "checkboxfield",
                                            boxLabel: "LLDP"
                                        },
                                        {
                                            name: "enable_box_discovery_oam",
                                            xtype: "checkboxfield",
                                            boxLabel: "OAM"
                                        },
                                        {
                                            name: "enable_box_discovery_rep",
                                            xtype: "checkboxfield",
                                            boxLabel: "REP"
                                        },
                                        {
                                            name: "enable_box_discovery_stp",
                                            xtype: "checkboxfield",
                                            boxLabel: "STP"
                                        },
                                        {
                                            name: "enable_box_discovery_udld",
                                            xtype: "checkboxfield",
                                            boxLabel: "UDLD"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            title: "Periodic discovery",
                            items: [
                                {
                                    name: "enable_periodic_discovery",
                                    xtype: "checkbox",
                                    boxLabel: "Enable"
                                },
                                {
                                    xtype: "fieldset",
                                    title: "Periodic discovery intervals",
                                    layout: "vbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "periodic_discovery_interval",
                                                    xtype: "numberfield",
                                                    fieldLabel: "Interval, sec",
                                                    allowBlank: false,
                                                    uiStyle: "small",
                                                    listeners: {
                                                        scope: me,
                                                        change: function(_item, newValue, oldValue, eOpts) {
                                                            me.form.findField("periodic_discovery_interval_calculated").setValue(newValue);
                                                        }
                                                    }
                                                },
                                                {
                                                    name: 'periodic_discovery_interval_calculated',
                                                    xtype: 'displayfield',
                                                    renderer: NOC.render.Duration
                                                }
                                            ]
                                        },
                                    ]
                                },
                                {
                                    xtype: "container",
                                    layout: {
                                        type: "table",
                                        columns: 4
                                    },
                                    defaults: {
                                        padding: "4 8 0 0"
                                    },
                                    items: [
                                        {
                                            name: "enable_periodic_discovery_uptime",
                                            xtype: "checkboxfield",
                                            boxLabel: "Uptime"
                                        },
                                        {
                                            name: "enable_periodic_discovery_interface_status",
                                            xtype: "checkboxfield",
                                            boxLabel: "Interface status"
                                        },
                                        {
                                            name: "enable_periodic_discovery_mac",
                                            xtype: "checkboxfield",
                                            boxLabel: "MAC"
                                        },
                                        {
                                            name: "enable_periodic_discovery_metrics",
                                            xtype: "checkboxfield",
                                            boxLabel: "Metrics"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            title: "Metrics",
                            items: [
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
                                            align: "right",
                                            renderer: NOC.render.Size
                                        },
                                        {
                                            text: "Low Warn",
                                            dataIndex: "low_warn",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right",
                                            renderer: NOC.render.Size
                                        },
                                        {
                                            text: "High Warn",
                                            dataIndex: "high_warn",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right",
                                            renderer: NOC.render.Size
                                        },
                                        {
                                            text: "High Error",
                                            dataIndex: "high_error",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right",
                                            renderer: NOC.render.Size
                                        }
                                    ]

                                }
                            ]
                        }
                    ],
                    formToolbar: [
                        me.validationSettingsButton
                    ]
                }
            ]
        });
        me.callParent();
    },
    //
    onValidationSettings: function () {
        var me = this;
        me.showItem(me.ITEM_VALIDATION_SETTINGS).preview(me.currentRecord);
    }
});
