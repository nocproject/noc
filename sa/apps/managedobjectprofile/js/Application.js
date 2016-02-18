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
        "Ext.ux.form.MultiIntervalField"
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
                    width: 60,
                    renderer: function(value, meta, record) {
                        var v = NOC.render.Bool(value);
                        if(value) {
                            v += " " + record.get("ping_interval");
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
                    text: "Box",
                    dataIndex: "enable_box_discovery",
                    width: 60,
                    renderer: NOC.render.Bool,
                    align: "center"
                },
                {
                    text: "Periodic",
                    dataIndex: "enable_periodic_discovery",
                    width: 60,
                    renderer: function(value, meta, record) {
                        var v = NOC.render.Bool(value);
                        if(value) {
                            v += " " + record.get("periodic_discovery_interval");
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
                        layout: "anchor"
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
                                    name: "ping_interval",
                                    xtype: "numberfield",
                                    fieldLabel: "Interval",
                                    uiStyle: "small"
                                }
                            ]
                        },
                        {
                            title: "FM",
                            items: [
                                {
                                    name: "down_severity",
                                    xtype: "numberfield",
                                    fieldLabel: "Down severity",
                                    allowBlank: false,
                                    uiStyle: "small"
                                },
                                {
                                    name: "check_link_interval",
                                    xtype: "multiintervalfield",
                                    fieldLabel: "check_link interval",
                                    allowBlank: true
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
                                    xtype: "container",
                                    layout: "hbox",
                                    defaults: {
                                        padding: "0 8 0 0"
                                    },
                                    items: [
                                        {
                                            name: "box_discovery_interval",
                                            xtype: "numberfield",
                                            fieldLabel: "Interval",
                                            allowBlank: false,
                                            uiStyle: "small",
                                        },
                                        {
                                            name: "box_discovery_failed_interval",
                                            xtype: "numberfield",
                                            fieldLabel: "Failed Interval",
                                            allowBlank: false,
                                            uiStyle: "small"
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
                                            uiStyle: "small"
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
                                            uiStyle: "small"
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
                                    name: "periodic_discovery_interval",
                                    xtype: "numberfield",
                                    fieldLabel: "Interval",
                                    allowBlank: false,
                                    uiStyle: "small"
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
