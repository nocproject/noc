//---------------------------------------------------------------------
// sa.managedobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.Application");

Ext.define("NOC.sa.managedobject.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.managedobject.Model",
        "NOC.sa.managedobject.AttributesModel",
        "NOC.sa.managedobject.LookupField",
        "NOC.sa.managedobject.SchemeLookupField",
        "NOC.sa.administrativedomain.LookupField",
        "NOC.main.pool.LookupField",
        "NOC.sa.managedobjectprofile.LookupField",
        "NOC.sa.managedobjectselector.LookupField",
        "NOC.vc.vcdomain.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.main.pyrule.LookupField",
        "NOC.main.ref.profile.LookupField",
        "NOC.main.ref.stencil.LookupField",
        "NOC.sa.authprofile.LookupField",
        "NOC.sa.terminationgroup.LookupField",
        "NOC.inv.networksegment.LookupField",
        "NOC.main.timepattern.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.fm.ttsystem.LookupField"
    ],
    model: "NOC.sa.managedobject.Model",
    search: true,
    rowClassField: "row_class",
    actions: [
        {
            title: __("Run discovery now"),
            action: "run_discovery",
            glyph: NOC.glyph.play
        },
        {
            title: __("Set managed"),
            action: "set_managed",
            glyph: NOC.glyph.check
        },
        {
            title: __("Set unmanaged"),
            action: "set_unmanaged",
            glyph: NOC.glyph.times
        }
    ],
    validationModelId: "sa.ManagedObject",
    //
    initComponent: function() {
        var me = this;

        me.configPreviewButton = Ext.create("Ext.button.Button", {
            text: __("Config"),
            glyph: NOC.glyph.file,
            scope: me,
            handler: me.onConfig
        });

        me.cardButton = Ext.create("Ext.button.Button", {
            text: __("Card"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onCard
        });

        me.dashboardButton = Ext.create("Ext.button.Button", {
            text: __("Dashboard"),
            glyph: NOC.glyph.line_chart,
            scope: me,
            tooltip: __("Show dashboard"),
            handler: me.onDashboard
        });

        me.showMapButton = Ext.create("Ext.button.Button", {
            text: __("Show Map"),
            glyph: NOC.glyph.globe,
            scope: me,
            handler: me.onShowMap
        });

        me.consoleButton = Ext.create("Ext.button.Button", {
            text: __("Console"),
            glyph: NOC.glyph.terminal,
            scope: me,
            handler: me.onConsole
        });

        me.scriptsButton = Ext.create("Ext.button.Button", {
            text: __("Scripts"),
            glyph: NOC.glyph.play,
            disabled: true,
            scope: me,
            handler: me.onScripts
        });

        me.interfacesButton = Ext.create("Ext.button.Button", {
            text: __("Interfaces"),
            glyph: NOC.glyph.reorder,
            scope: me,
            handler: me.onInterfaces
        });

        me.linksButton = Ext.create("Ext.button.Button", {
            text: __("Links"),
            glyph: NOC.glyph.link,
            scope: me,
            handler: me.onLinks
        });

        me.discoveryButton = Ext.create("Ext.button.Button", {
            text: __("Discovery"),
            glyph: NOC.glyph.search,
            scope: me,
            handler: me.onDiscovery
        });

        me.alarmsButton = Ext.create("Ext.button.Button", {
            text: __("Alarms"),
            glyph: NOC.glyph.exclamation_triangle,
            scope: me,
            handler: me.onAlarm
        });

        me.inventoryButton = Ext.create("Ext.button.Button", {
            text: __("Inventory"),
            glyph: NOC.glyph.list,
            scope: me,
            handler: me.onInventory
        });

        me.interactionsButton = Ext.create("Ext.button.Button", {
            text: __("Command Log"),
            glyph: NOC.glyph.film,
            scope: me,
            handler: me.onInteractions
        });

        me.validationSettingsButton = Ext.create("Ext.button.Button", {
            text: __("Validation"),
            glyph: NOC.glyph.file,
            scope: me,
            handler: me.onValidationSettings
        });


        me.capsButton = Ext.create("Ext.button.Button", {
            text: __("Capabilities"),
            glyph: NOC.glyph.file,
            scope: me,
            handler: me.onCaps
        });

        me.factsButton = Ext.create("Ext.button.Button", {
            text: __("Facts"),
            glyph: NOC.glyph.file,
            scope: me,
            handler: me.onFacts
        });

        me.ITEM_CONFIG = me.registerItem(
            Ext.create("NOC.core.RepoPreview", {
                app: me,
                previewName: '{0} config',
                restUrl: '/sa/managedobject/{0}/repo/cfg/',
                historyHashPrefix: "config"
            })
        );

        me.ITEM_CONSOLE = me.registerItem(
            Ext.create("NOC.sa.managedobject.ConsolePanel", {app: me})
        );
        me.ITEM_INVENTORY = me.registerItem("NOC.sa.managedobject.InventoryPanel");
        me.ITEM_INTERFACE = me.registerItem("NOC.sa.managedobject.InterfacePanel");
        me.ITEM_SCRIPTS = me.registerItem("NOC.sa.managedobject.ScriptPanel");
        me.ITEM_LINKS = me.registerItem("NOC.sa.managedobject.LinksPanel");

        me.ITEM_DISCOVERY = me.registerItem(
            Ext.create("NOC.sa.managedobject.DiscoveryPanel", {app: me})
        );

        me.ITEM_ALARM = me.registerItem("NOC.sa.managedobject.AlarmPanel");
        me.ITEM_INTERACTIONS = me.registerItem("NOC.sa.managedobject.InteractionsPanel");

        me.ITEM_VALIDATION_SETTINGS = me.registerItem(
            Ext.create("NOC.cm.validationpolicysettings.ValidationSettingsPanel", {
                app: me,
                validationModelId: me.validationModelId
            })
        );

        me.ITEM_CAPS = me.registerItem("NOC.sa.managedobject.CapsPanel");
        me.ITEM_FACTS = me.registerItem("NOC.sa.managedobject.FactsPanel");

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 130
                },
                {
                    text: __("Managed"),
                    dataIndex: "is_managed",
                    width: 30,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Segment"),
                    dataIndex: "segment",
                    width: 150,
                    renderer: NOC.render.Lookup("segment")
                },
                {
                    text: __("Platform"),
                    dataIndex: "platform",
                    width: 150
                },
                {
                    text: __("SA Profile"),
                    dataIndex: "profile_name"
                },
                {
                    text: __("Obj. Profile"),
                    dataIndex: "object_profile",
                    renderer: NOC.render.Lookup("object_profile")
                },
                {
                    text: __("Adm. Domain"),
                    dataIndex: "administrative_domain",
                    renderer: NOC.render.Lookup("administrative_domain"),
                    width: 100
                },
                {
                    text: __("Auth Profile"),
                    dataIndex: "auth_profile",
                    renderer: NOC.render.Lookup("auth_profile"),
                    width: 100
                },
                {
                    text: __("VRF"),
                    dataIndex: "vrf",
                    renderer: NOC.render.Lookup("vrf"),
                    width: 100
                },
                {
                    text: __("Address"),
                    dataIndex: "address"
                },
                {
                    text: __("Pool"),
                    dataIndex: "pool",
                    renderer: NOC.render.Lookup("pool"),
                    width: 100
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    width: 100
                },
                {
                    text: __("Interfaces"),
                    dataIndex: "interface_count",
                    width: 50,
                    sortable: false,
                    align: "right",
                    renderer: NOC.render.Clickable,
                    onClick: me.onInterfaceClick
                },
                {
                    text: __("Links"),
                    dataIndex: "link_count",
                    width: 50,
                    sortable: false,
                    align: "right",
                    renderer: NOC.render.Clickable,
                    onClick: me.onLinkClick
                },
                {
                    text: __("Tags"),
                    dataIndex: "tags",
                    renderer: NOC.render.Tags,
                    width: 100
                }
            ],
            fields: [
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    border: false,
                    padding: 0,
                    items: [
                        {
                            name: "name",
                            xtype: "textfield",
                            fieldLabel: __("Name"),
                            allowBlank: false,
                            uiStyle: "large"
                        },
                        {
                            name: "is_managed",
                            xtype: "checkboxfield",
                            boxLabel: __("Is Managed?"),
                            allowBlank: false,
                            groupEdit: true,
                            padding: "0px 0px 0px 4px"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    border: false,
                    padding: 0,
                    items: [
                        {
                            name: "platform",
                            xtype: "displayfield",
                            fieldLabel: __("Platform"),
                            allowBlank: true
                        },
                        {
                            name: "version",
                            xtype: "displayfield",
                            fieldLabel: __("Version"),
                            labelWidth: 55,
                            padding: "0px 0px 0px 4px",
                            allowBlank: true
                        }
                    ]
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true,
                    uiStyle: "extra"
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Role"),
                    defaults: {
                        padding: 4
                    },
                    items: [
                        {
                            name: "object_profile",
                            xtype: "sa.managedobjectprofile.LookupField",
                            fieldLabel: __("Object Profile"),
                            labelWidth: 90,
                            itemId: "object_profile",
                            allowBlank: false,
                            groupEdit: true
                        },
                        {
                            name: "shape",
                            xtype: "main.ref.stencil.LookupField",
                            fieldLabel: __("Shape"),
                            allowBlank: true,
                            groupEdit: true,
                            labelWidth: 40
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Location"),
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "administrative_domain",
                            xtype: "sa.administrativedomain.LookupField",
                            fieldLabel: __("Administrative Domain"),
                            width: 200,
                            allowBlank: false,
                            groupEdit: true
                        },
                        {
                            name: "segment",
                            xtype: "inv.networksegment.LookupField",
                            fieldLabel: __("Segment"),
                            width: 200,
                            allowBlank: false,
                            groupEdit: true
                        },
                        {
                            name: "pool",
                            xtype: "main.pool.LookupField",
                            fieldLabel: __("Pool"),
                            width: 100,
                            allowBlank: false,
                            groupEdit: true
                        },
                        {
                            name: "vrf",
                            xtype: "ip.vrf.LookupField",
                            fieldLabel: __("VRF"),
                            allowBlank: true,
                            groupEdit: true
                        },
                        {
                            name: "vc_domain",
                            xtype: "vc.vcdomain.LookupField",
                            fieldLabel: __("VC Domain"),
                            allowBlank: true,
                            groupEdit: true
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Access"),
                    items: [
                        {
                            xtype: "container",
                            layout: "hbox",
                            defaults: {
                                labelAlign: "top",
                                padding: 4
                            },
                            items: [
                                {
                                    name: "profile_name",
                                    xtype: "main.ref.profile.LookupField",
                                    fieldLabel: __("SA Profile"),
                                    allowBlank: false,
                                    groupEdit: true
                                },
                                {
                                    name: "scheme",
                                    xtype: "sa.managedobject.SchemeLookupField",
                                    fieldLabel: __("Scheme"),
                                    allowBlank: false,
                                    uiStyle: "small",
                                    groupEdit: true
                                },
                                {
                                    name: "address",
                                    xtype: "textfield",
                                    fieldLabel: __("Address"),
                                    allowBlank: false,
                                    uiStyle: "medium"
                                },
                                {
                                    name: "port",
                                    xtype: "numberfield",
                                    fieldLabel: __("Port"),
                                    allowBlank: true,
                                    uiStyle: "small",
                                    minValue: 0,
                                    maxValue: 65535,
                                    hideTrigger: true
                                },
                                {
                                    name: "max_scripts",
                                    xtype: "numberfield",
                                    fieldLabel: __("Max. Scripts"),
                                    allowBlank: true,
                                    uiStyle: "small",
                                    hideTrigger: true,
                                    minValue: 0,
                                    maxValue: 99
                                },
                                {
                                    name: "time_pattern",
                                    xtype: "main.timepattern.LookupField",
                                    fieldLabel: __("Time Pattern"),
                                    allowBlank: true,
                                    groupEdit: true,
                                    uiStyle: "medium"
                                }
                            ]
                        },
                        {
                            xtype: "container",
                            layout: "hbox",
                            defaults: {
                                labelAlign: "top",
                                padding: 4
                            },
                            items: [
                                {
                                    name: "auth_profile",
                                    xtype: "sa.authprofile.LookupField",
                                    fieldLabel: __("Auth Profile"),
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "user",
                                    xtype: "textfield",
                                    fieldLabel: __("User"),
                                    allowBlank: true,
                                    groupEdit: true,
                                    uiStyle: "medium"
                                },
                                {
                                    name: "password",
                                    xtype: "textfield",
                                    fieldLabel: __("Password"),
                                    allowBlank: true,
                                    inputType: "password",
                                    groupEdit: true,
                                    uiStyle: "medium"
                                },
                                {
                                    name: "super_password",
                                    xtype: "textfield",
                                    fieldLabel: __("Super Password"),
                                    allowBlank: true,
                                    inputType: "password",
                                    groupEdit: true,
                                    uiStyle: "medium"
                                },
                                {
                                    name: "remote_path",
                                    xtype: "textfield",
                                    fieldLabel: __("Path"),
                                    allowBlank: true,
                                    uiStyle: "medium"
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Service"),
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "termination_group",
                            xtype: "sa.terminationgroup.LookupField",
                            fieldLabel: __("Termination Group"),
                            allowBlank: true,
                            groupEdit: true
                        },
                        {
                            name: "service_terminator",
                            xtype: "sa.terminationgroup.LookupField",
                            fieldLabel: __("Service Terminator"),
                            allowBlank: true,
                            groupEdit: true
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("CPE"),
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "controller",
                            xtype: "sa.managedobject.LookupField",
                            fieldLabel: __("Controller"),
                            allowBlank: true,
                            groupEdit: true
                        },
                        {
                            name: "local_cpe_id",
                            xtype: "textfield",
                            fieldLabel: __("Local CPE Id"),
                            allowBlank: true
                        },
                        {
                            name: "global_cpe_id",
                            xtype: "textfield",
                            fieldLabel: __("Global CPE Id"),
                            allowBlank: true
                        },
                        {
                            name: "last_seen",
                            xtype: "displayfield",
                            fieldLabel: __("Last Seen"),
                            allowBlank: true
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Event Sources"),
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "trap_source_type",
                            xtype: "combobox",
                            fieldLabel: __("Trap Source"),
                            store: [
                                ["d", "Disable"],
                                ["m", "Management Address"],
                                ["s", "Specify address"],
                                ["l", "Loopback address"],
                                ["a", "All interface addresses"]
                            ],
                            value: "d",
                            listeners: {
                                scope: me,
                                change: function(combo, newValue, oldValue, eOpts) {
                                    combo.nextSibling().setHidden(newValue !== "s");
                                },
                                afterrender: function(combo, eOpts) {
                                    combo.nextSibling().setHidden(combo.value !== "s");
                                }
                            }
                        },
                        {
                            name: "trap_source_ip",
                            xtype: "textfield",
                            fieldLabel: __("Trap Source IP"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "syslog_source_type",
                            xtype: "combobox",
                            fieldLabel: __("Syslog Source"),
                            store: [
                                ["d", "Disable"],
                                ["m", "Management Address"],
                                ["s", "Specify address"],
                                ["l", "Loopback address"],
                                ["a", "All interface addresses"]
                            ],
                            value: "d",
                            listeners: {
                                scope: me,
                                change: function(combo, newValue, oldValue, eOpts) {
                                    combo.nextSibling().setHidden(newValue !== "s");
                                },
                                afterrender: function(combo, eOpts) {
                                    combo.nextSibling().setHidden(combo.value !== "s");
                                }
                            }
                        },
                        {
                            name: "syslog_source_ip",
                            xtype: "textfield",
                            fieldLabel: __("Syslog Source IP"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: "SNMP",
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "trap_community",
                            xtype: "textfield",
                            fieldLabel: __("Trap Community"),
                            allowBlank: true,
                            groupEdit: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "snmp_ro",
                            xtype: "textfield",
                            fieldLabel: __("RO Community"),
                            allowBlank: true,
                            groupEdit: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "snmp_rw",
                            xtype: "textfield",
                            fieldLabel: __("RW Community"),
                            allowBlank: true,
                            groupEdit: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Rules"),
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "config_filter_rule",
                            xtype: "main.pyrule.LookupField",
                            fieldLabel: __("Config Filter pyRule"),
                            allowBlank: true,
                            groupEdit: true
                        },
                        {
                            name: "config_diff_filter_rule",
                            xtype: "main.pyrule.LookupField",
                            fieldLabel: __("Config Diff Filter Rule"),
                            allowBlank: true,
                            groupEdit: true
                        },
                        {
                            name: "config_validation_rule",
                            xtype: "main.pyrule.LookupField",
                            fieldLabel: __("Config Validation pyRule"),
                            allowBlank: true,
                            groupEdit: true
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        labelAlign: "top",
                        padding: 4
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
                            xtype: "textfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Escalation"),
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "escalation_policy",
                            xtype: "combobox",
                            fieldLabel: __("Escalation Policy"),
                            allowBlank: true,
                            uiStyle: "medium",
                            store: [
                                ["P", __("Profile")],
                                ["E", __("Enable")],
                                ["D", __("Disable")],
                                ["R", __("As Depended")]
                            ],
                            value: "P"
                        },
                        {
                            name: "tt_system",
                            xtype: "fm.ttsystem.LookupField",
                            fieldLabel: __("TT System"),
                            allowBlank: true
                        },
                        {
                            name: "tt_queue",
                            xtype: "textfield",
                            fieldLabel: __("TT Queue"),
                            allowBlank: true
                        },
                        {
                            name: "tt_system_id",
                            xtype: "textfield",
                            fieldLabel: __("TT System ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Discovery Alarm"),
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "box_discovery_alarm_policy",
                            xtype: "combobox",
                            fieldLabel: __("Box Alarm"),
                            allowBlank: true,
                            uiStyle: "medium",
                            store: [
                                ["P", __("Profile")],
                                ["E", __("Enable")],
                                ["D", __("Disable")]
                            ],
                            value: "P"
                        },
                        {
                            name: "periodic_discovery_alarm_policy",
                            xtype: "combobox",
                            fieldLabel: __("Periodic Alarm"),
                            allowBlank: true,
                            uiStyle: "medium",
                            store: [
                                ["P", __("Profile")],
                                ["E", __("Enable")],
                                ["D", __("Disable")]
                            ],
                            value: "P"
                        }
                    ]
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: __("Tags"),
                    allowBlank: true,
                    uiStyle: "extra"
                }
            ],
            formToolbar: [
                me.cardButton,
                me.dashboardButton,
                me.showMapButton,
                me.consoleButton,
                me.scriptsButton,
                me.configPreviewButton,
                me.inventoryButton,
                me.interfacesButton,
                me.linksButton,
                me.discoveryButton,
                me.alarmsButton,
                me.interactionsButton,
                me.validationSettingsButton,
                me.capsButton,
                me.factsButton
            ]
        });
        me.callParent();
    },
    filters: [
        // @todo: By SA Profile
        {
            title: __("By Managed"),
            name: "is_managed",
            ftype: "boolean"
        },
        {
            title: __("By SA Profile"),
            name: "profile_name",
            ftype: "lookup",
            lookup: "main.ref.profile"
        },
        {
            title: __("By Obj. Profile"),
            name: "object_profile",
            ftype: "lookup",
            lookup: "sa.managedobjectprofile"
        },
        {
            title: __("By Adm. Domain"),
            name: "administrative_domain",
            ftype: "tree",
            lookup: "sa.administrativedomain"
        },
        {
            title: __("By Segment"),
            name: "segment",
            ftype: "tree",
            lookup: "inv.networksegment"
        },
        {
            title: __("By Selector"),
            name: "selector",
            ftype: "lookup",
            lookup: "sa.managedobjectselector"
        },
        {
            title: __("By Pool"),
            name: "pool",
            ftype: "lookup",
            lookup: "main.pool"
        },
        {
            title: __("By VRF"),
            name: "vrf",
            ftype: "lookup",
            lookup: "ip.vrf"
        },
        {
            title: __("By VC Domain"),
            name: "vc_domain",
            ftype: "lookup",
            lookup: "vc.vcdomain"
        },
        {
            title: __("By Controller"),
            name: "controller",
            ftype: "lookup",
            lookup: "sa.managedobject"
        },
        {
            title: __("By Termination Group"),
            name: "termination_group",
            ftype: "lookup",
            lookup: "sa.terminationgroup"
        },
        {
            title: __("By Service Terminator"),
            name: "service_terminator",
            ftype: "lookup",
            lookup: "sa.terminationgroup"
        },
        {
            title: __("By Tags"),
            name: "tags",
            ftype: "tag"
        }
    ],
    inlines: [
        {
            title: __("Attributes"),
            model: "NOC.sa.managedobject.AttributesModel",
            columns: [
                {
                    text: __("Key"),
                    dataIndex: "key",
                    width: 100,
                    editor: "textfield"
                },
                {
                    text: __("Value"),
                    dataIndex: "value",
                    editor: "textfield",
                    flex: 1
                }
            ]
        }
    ],
    //
    onCard: function() {
        var me = this;
        if(me.currentRecord) {
            window.open(
                "/api/card/view/managedobject/" + me.currentRecord.get("id") + "/"
            );
        }
    },
    //
    onDashboard: function() {
        var me = this;
        if(me.currentRecord) {
            window.open(
                "/ui/grafana/dashboard/script/noc.js?dashboard=mo&id=" + me.currentRecord.get("id")
            );
        }
    },
    //
    onShowMap: function() {
        var me = this;
        NOC.launch("inv.map", "history", {
            args: [me.currentRecord.get("segment")]
        });
    },
    //
    onConsole: function() {
        var me = this;
        me.showItem(me.ITEM_CONSOLE).preview(me.currentRecord);
    },
    //
    onInteractions: function() {
        var me = this;
        me.showItem(me.ITEM_INTERACTIONS).preview(me.currentRecord);
    },
    //
    onConfig: function() {
        var me = this;
        me.previewItem(me.ITEM_CONFIG, me.currentRecord);
    },
    //
    onInventory: function() {
        var me = this;
        me.previewItem(me.ITEM_INVENTORY, me.currentRecord);
    },
    //
    onInterfaces: function() {
        var me = this;
        me.previewItem(me.ITEM_INTERFACE, me.currentRecord);
    },
    //
    onScripts: function() {
        var me = this;
        me.previewItem(me.ITEM_SCRIPTS, me.currentRecord);
    },
    //
    onLinks: function() {
        var me = this;
        me.previewItem(me.ITEM_LINKS, me.currentRecord);
    },
    //
    onDiscovery: function() {
        var me = this;
        me.showItem(me.ITEM_DISCOVERY).preview(me.currentRecord);
    },
    //
    onAlarm: function() {
        var me = this;
        me.previewItem(me.ITEM_ALARM, me.currentRecord);
    },
    //
    onCaps: function() {
        var me = this;
        me.previewItem(me.ITEM_CAPS, me.currentRecord);
    },
    //
    onFacts: function() {
        var me = this;
        me.previewItem(me.ITEM_FACTS, me.currentRecord);
    },
    //
    onInterfaceClick: function(record) {
        var me = this;
        me.previewItem(me.ITEM_INTERFACE, record);
    },
    //
    onLinkClick: function(record) {
        var me = this;
        me.previewItem(me.ITEM_LINKS, record);
    },
    //
    onValidationSettings: function () {
        var me = this;
        me.showItem(me.ITEM_VALIDATION_SETTINGS).preview(me.currentRecord);
    },
    //
    showForm: function() {
        var me = this;
        me.callParent();
        // Change button's visibility
        var disabled = !me.currentRecord;
        me.consoleButton.setDisabled(disabled || !NOC.hasPermission("console") || !me.currentRecord.get("is_managed"));
        me.scriptsButton.setDisabled(disabled || !NOC.hasPermission("script") || !me.currentRecord.get("is_managed"));
        me.configPreviewButton.setDisabled(disabled);
        me.interfacesButton.setDisabled(disabled);
        me.linksButton.setDisabled(disabled);
        me.discoveryButton.setDisabled(disabled || !me.currentRecord.get("is_managed"));
        me.alarmsButton.setDisabled(disabled || !me.currentRecord.get("is_managed"));

    },
    //
    // Possible values
    // [<id>] -- Show object's card
    // [<id>, "config" ] -- show object's config
    // [<id>, "config", <rev>] -- show revision
    // [<id>, "config", <rev1>, <rev2>] -- show diff
    //
    restoreHistory: function(args) {
        var me = this;
        me.loadById(args[0], function(record) {
            me.onEditRecord(record);
            switch (args[1]) {
                case "config":
                    switch(args.length) {
                        case 2:
                            me.onConfig();
                            break;
                        case 3:
                            me.onConfig();
                            // @todo: Fix
                            me.showItem(me.ITEM_CONFIG).historyRevision(record, args[2]);
                            break;
                        case 4:
                            me.showItem(me.ITEM_CONFIG).historyDiff(record, args[2], args[3]);
                            break;
                    }
                    break;
                case "facts":
                    me.onFacts();
                    break;
                case "interfaces":
                    me.onInterfaces();
                    break;
                case "links":
                    me.onLinks();
                    break;
            }
        });
    }
});
