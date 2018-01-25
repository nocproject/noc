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
        "NOC.sa.profile.LookupField",
        "NOC.inv.vendor.LookupField",
        "NOC.inv.platform.LookupField",
        "NOC.inv.firmware.LookupField",
        "NOC.sa.managedobjectprofile.LookupField",
        "NOC.sa.managedobjectselector.LookupField",
        "NOC.vc.vcdomain.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.main.pyrule.LookupField",
        "NOC.main.ref.stencil.LookupField",
        "NOC.sa.authprofile.LookupField",
        "NOC.sa.terminationgroup.LookupField",
        "NOC.inv.networksegment.LookupField",
        "NOC.main.timepattern.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.fm.ttsystem.LookupField",
        "NOC.inv.platform.LookupField",
        "NOC.inv.map.Maintenance",
        "NOC.maintenance.maintenancetype.LookupField"
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
    formMinWidth: 800,
    formMaxWidth: 1000,
    //
    initComponent: function() {
        var me = this,
            padding = 10,
            fieldSetDefaults = {
                xtype: "container",
                padding: padding,
                layout: "form",
                columnWidth: 0.5
            };
        me.actions.push(
            {
                title: __("New Maintaince"),
                glyph: NOC.glyph.wrench,
                run: me.newMaintaince
            },
            {
                title: __("Add to Maintaince"),
                glyph: NOC.glyph.plus,
                run: me.addToMaintaince
            }
        );
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

        me.maintainceButton = Ext.create("Ext.button.Button", {
            text: __("New Maintaince"),
            glyph: NOC.glyph.wrench,
            scope: me,
            handler: me.onMaintaince
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
                previewName: "{0} config",
                restUrl: "/sa/managedobject/{0}/repo/cfg/",
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
                    width: 150,
                    renderer: NOC.render.Lookup("platform")
                },
                {
                    text: __("SA Profile"),
                    dataIndex: "profile",
                    renderer: NOC.render.Lookup("profile")
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
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    border: false,
                    items: [
                        {
                            xtype: "container",
                            items: [ // first column
                                {
                                    name: "name",
                                    xtype: "textfield",
                                    fieldLabel: __("Name"),
                                    allowBlank: false,
                                    autoFocus: true,
                                    tabIndex: 10
                                    // uiStyle: "large"
                                },
                                {
                                    name: "description",
                                    xtype: "textarea",
                                    fieldLabel: __("Description"),
                                    allowBlank: true
                                    // uiStyle: "extra"
                                },
                                {
                                    name: "is_managed",
                                    xtype: "checkboxfield",
                                    fieldLabel: __("Is Managed?"),
                                    allowBlank: true,
                                    groupEdit: true
                                    // width: 200,
                                    // padding: "0px 0px 0px 4px"
                                }
                            ]
                        }, {
                            xtype: "container",
                            items: [ // second column
                                {
                                    name: "bi_id",
                                    xtype: "displayfield",
                                    fieldLabel: __("BI ID"),
                                    allowBlank: true
                                    // uiStyle: "medium"
                                },
                                {
                                    name: "tags",
                                    xtype: "tagsfield",
                                    fieldLabel: __("Tags"),
                                    allowBlank: true
                                    // uiStyle: "extra"
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Role"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "object_profile",
                                    xtype: "sa.managedobjectprofile.LookupField",
                                    fieldLabel: __("Object Profile"),
                                    itemId: "object_profile",
                                    allowBlank: false,
                                    tabIndex: 20,
                                    groupEdit: true
                                }]
                        },
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "shape",
                                    xtype: "main.ref.stencil.LookupField",
                                    fieldLabel: __("Shape"),
                                    allowBlank: true,
                                    groupEdit: true
                                }]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Platform"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "profile",
                                    xtype: "sa.profile.LookupField",
                                    fieldLabel: __("SA Profile"),
                                    allowBlank: false,
                                    tabIndex: 30,
                                    groupEdit: true
                                }, {
                                    name: "vendor",
                                    xtype: "inv.vendor.LookupField",
                                    fieldLabel: __("Vendor"),
                                    allowBlank: true,
                                    groupEdit: true
                                }, {
                                    name: "platform",
                                    xtype: "inv.platform.LookupField",
                                    fieldLabel: __("Platform"),
                                    allowBlank: true,
                                    groupEdit: true
                                }
                            ]
                        }, {
                            xtype: "container",
                            items: [
                                {
                                    name: "version",
                                    xtype: "inv.firmware.LookupField",
                                    fieldLabel: __("Version"),
                                    allowBlank: true,
                                    groupEdit: true
                                }, {
                                    name: "software_image",
                                    xtype: "displayfield",
                                    fieldLabel: __("Software Image"),
                                    allowBlank: true
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Access"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "scheme",
                                    xtype: "sa.managedobject.SchemeLookupField",
                                    fieldLabel: __("Scheme"),
                                    allowBlank: false,
                                    tabIndex: 40,
                                    // uiStyle: "small",
                                    groupEdit: true
                                },
                                {
                                    name: "address",
                                    xtype: "textfield",
                                    fieldLabel: __("Address"),
                                    allowBlank: false,
                                    tabIndex: 50
                                    // uiStyle: "medium"
                                },
                                {
                                    name: "access_preference",
                                    xtype: "combobox",
                                    fieldLabel: __("Access Preference"),
                                    allowBlank: true,
                                    // uiStyle: "medium",
                                    store: [
                                        ["P", __("Profile")],
                                        ["S", __("SNMP Only")],
                                        ["C", __("CLI Only")],
                                        ["SC", __("SNMP, CLI")],
                                        ["CS", __("CLI, SNMP")]
                                    ],
                                    value: "P"
                                },
                                {
                                    name: "port",
                                    xtype: "numberfield",
                                    fieldLabel: __("Port"),
                                    allowBlank: true,
                                    // uiStyle: "small",
                                    minValue: 0,
                                    maxValue: 65535,
                                    hideTrigger: true

                                },
                                {
                                    name: "cli_session_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("CLI Session Policy"),
                                    allowBlank: true,
                                    // uiStyle: "medium",
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    value: "P"
                                },
                                {
                                    name: "cli_privilege_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("CLI Privilege Policy"),
                                    allowBlank: true,
                                    // uiStyle: "medium",
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Raise Privileges")],
                                        ["D", __("Don't Raise")]
                                    ],
                                    value: "P"
                                },
                                {
                                    name: "remote_path",
                                    xtype: "textfield",
                                    fieldLabel: __("Path"),
                                    allowBlank: true
                                    // uiStyle: "medium"
                                }
                            ]
                        },
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "auth_profile",
                                    xtype: "sa.authprofile.LookupField",
                                    fieldLabel: __("Auth Profile"),
                                    tabIndex: 60,
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "user",
                                    xtype: "textfield",
                                    fieldLabel: __("User"),
                                    tabIndex: 61,
                                    allowBlank: true,
                                    groupEdit: true
                                    // uiStyle: "medium"
                                },
                                {
                                    name: "password",
                                    xtype: "textfield",
                                    fieldLabel: __("Password"),
                                    tabIndex: 62,
                                    allowBlank: true,
                                    inputType: "password",
                                    groupEdit: true
                                    // uiStyle: "medium"
                                },
                                {
                                    name: "super_password",
                                    xtype: "textfield",
                                    fieldLabel: __("Super Password"),
                                    allowBlank: true,
                                    inputType: "password",
                                    groupEdit: true
                                    // uiStyle: "medium"
                                },
                                {
                                    name: "snmp_ro",
                                    xtype: "textfield",
                                    fieldLabel: __("RO Community"),
                                    tabIndex: 63,
                                    allowBlank: true,
                                    groupEdit: true
                                    // uiStyle: "medium"
                                },
                                {
                                    name: "snmp_rw",
                                    xtype: "textfield",
                                    fieldLabel: __("RW Community"),
                                    tabIndex: 64,
                                    allowBlank: true,
                                    groupEdit: true
                                    // uiStyle: "medium"
                                },
                                {
                                    name: "max_scripts",
                                    xtype: "numberfield",
                                    fieldLabel: __("Max. Scripts"),
                                    allowBlank: true,
                                    // uiStyle: "small",
                                    hideTrigger: true,
                                    minValue: 0,
                                    maxValue: 99
                                },
                                {
                                    name: "time_pattern",
                                    xtype: "main.timepattern.LookupField",
                                    fieldLabel: __("Time Pattern"),
                                    allowBlank: true,
                                    groupEdit: true
                                    // uiStyle: "medium"
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Location"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "administrative_domain",
                                    xtype: "sa.administrativedomain.LookupField",
                                    fieldLabel: __("Administrative Domain"),
                                    allowBlank: false,
                                    tabIndex: 90,
                                    groupEdit: true
                                },
                                {
                                    name: "segment",
                                    xtype: "inv.networksegment.LookupField",
                                    fieldLabel: __("Segment"),
                                    allowBlank: false,
                                    tabIndex: 100,
                                    groupEdit: true
                                },
                                {
                                    name: "pool",
                                    xtype: "main.pool.LookupField",
                                    fieldLabel: __("Pool"),
                                    allowBlank: false,
                                    tabIndex: 110,
                                    groupEdit: true
                                }
                            ]
                        }, {
                            xtype: "container",
                            items: [
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
                                },
                                {
                                    name: "autosegmentation_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Autosegmentation Policy"),
                                    allowBlank: true,
                                    groupEdit: true,
                                    store: [
                                        ["p", __("Profile")],
                                        ["d", __("Do not segmentate")],
                                        ["e", __("Allow autosegmentation")],
                                        ["o", __("Segmentate to existing segment")],
                                        ["c", __("Segmentate to child segment")]
                                    ],
                                    value: "p"
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Event Sources"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "event_processing_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Event Policy"),
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    value: "P",
                                    allowBlank: false,
                                    tabIndex: 130
                                    // uiStyle: "medium"
                                },
                                {
                                    name: "trap_source_type",
                                    xtype: "combobox",
                                    fieldLabel: __("Trap Source"),
                                    store: [
                                        ["d", __("Disable")],
                                        ["m", __("Management Address")],
                                        ["s", __("Specify address")],
                                        ["l", __("Loopback address")],
                                        ["a", __("All interface addresses")]
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
                                    allowBlank: true
                                    // uiStyle: "medium"
                                }]
                        }, {
                            xtype: "container",
                            items: [
                                {
                                    name: "syslog_source_type",
                                    xtype: "combobox",
                                    fieldLabel: __("Syslog Source"),
                                    store: [
                                        ["d", __("Disable")],
                                        ["m", __("Management Address")],
                                        ["s", __("Specify address")],
                                        ["l", __("Loopback address")],
                                        ["a", __("All interface addresses")]
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
                                    allowBlank: true
                                    // uiStyle: "medium"
                                },
                                {
                                    name: "trap_community",
                                    xtype: "textfield",
                                    fieldLabel: __("Trap Community"),
                                    allowBlank: true,
                                    groupEdit: true
                                    // uiStyle: "medium"
                                }]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Service"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "termination_group",
                                    xtype: "sa.terminationgroup.LookupField",
                                    fieldLabel: __("Termination Group"),
                                    allowBlank: true,
                                    groupEdit: true
                                }
                            ]
                        },
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "service_terminator",
                                    xtype: "sa.terminationgroup.LookupField",
                                    fieldLabel: __("Service Terminator"),
                                    allowBlank: true,
                                    groupEdit: true
                                }]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("CPE"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
                            xtype: "container",
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
                                }]
                        },
                        {
                            xtype: "container",
                            items: [
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
                                }]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Rules"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
                            xtype: "container",
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
                                }]
                        }, {
                            xtype: "container",
                            items: [
                                {
                                    name: "config_validation_rule",
                                    xtype: "main.pyrule.LookupField",
                                    fieldLabel: __("Config Validation pyRule"),
                                    allowBlank: true,
                                    groupEdit: true
                                }]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Integration"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
                            xtype: "container",
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
                                    allowBlank: true
                                    // uiStyle: "medium"
                                }]
                        }, {
                            xtype: "container",
                            items: []
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Escalation"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "escalation_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Escalation Policy"),
                                    allowBlank: true,
                                    // uiStyle: "medium",
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
                                }]
                        }, {
                            xtype: "container",
                            items: [
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
                                    allowBlank: true
                                    // uiStyle: "medium"
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Discovery Alarm"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "box_discovery_alarm_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Box Alarm"),
                                    allowBlank: true,
                                    // uiStyle: "medium",
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    value: "P"
                                }]
                        }, {
                            xtype: "container",
                            items: [
                                {
                                    name: "periodic_discovery_alarm_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Periodic Alarm"),
                                    allowBlank: true,
                                    // uiStyle: "medium",
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    value: "P"
                                }]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Telemetry"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "box_discovery_telemetry_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Box Telemetry"),
                                    allowBlank: true,
                                    // uiStyle: "medium",
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    value: "P"
                                },
                                {
                                    name: "box_discovery_telemetry_sample",
                                    xtype: "numberfield",
                                    fieldLabel: __("Box Sample")
                                    // uiStyle: "medium"
                                }]
                        }, {
                            xtype: "container",
                            items: [
                                {
                                    name: "periodic_discovery_telemetry_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Periodic Alarm"),
                                    allowBlank: true,
                                    // uiStyle: "medium",
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    value: "P"
                                },
                                {
                                    name: "periodic_discovery_telemetry_sample",
                                    xtype: "numberfield",
                                    fieldLabel: __("Periodic Sample")
                                    // uiStyle: "medium"
                                }]
                        }
                    ]
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
                me.maintainceButton,
                me.interactionsButton,
                me.validationSettingsButton,
                me.capsButton,
                me.factsButton
            ]
        })
        ;
        me.callParent();
    },
    filters: [
        {
            title: __("By Managed"),
            name: "is_managed",
            ftype: "boolean"
        },
        {
            title: __("By SA Profile"),
            name: "profile",
            ftype: "lookup",
            lookup: "sa.profile"
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
            title: __("Platform"),
            name: "platform",
            ftype: "lookup",
            lookup: "inv.platform"
        },
        {
            title: __("By Tags"),
            name: "tags",
            ftype: "tag"
        }
    ],
    inlines:
        [{
            title: __("Attributes"),
            collapsed: true,
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
        }],
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
    onMaintaince: function() {
        var me = this;
        me.newMaintaince([{
            object: me.currentRecord.get("id"),
            object__label: me.currentRecord.get("name")
        }]);
    },
    //
    addToMaintaince: function(objects) {
        NOC.run(
            'NOC.inv.map.Maintenance',
            __('Add To Maintenance'),
            {
                args: [
                    {mode: 'Object'},
                    objects
                ]
            }
        );
    },
    //
    newMaintaince: function(objects) {
        var args = {
            direct_objects: objects,
            subject: __('created from managed objects list at ') + Ext.Date.format(new Date(), 'd.m.Y H:i P'),
            contacts: NOC.username,
            start_date: Ext.Date.format(new Date(), 'd.m.Y'),
            start_time: Ext.Date.format(new Date(), 'H:i'),
            stop_time: '12:00',
            suppress_alarms: true
        };
        Ext.create("NOC.maintenance.maintenancetype.LookupField")
        .getStore()
        .load({
            params: {__query: 'РНР'},
            callback: function(records) {
                if(records.length > 0) {
                    Ext.apply(args, {
                        type: records[0].id
                    })
                }
                NOC.launch("maintenance.maintenance", "new", {
                    args: args
                });
            }
        });
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
    onValidationSettings: function() {
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
        me.maintainceButton.setDisabled(disabled || !me.currentRecord.get("is_managed"));

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
            switch(args[1]) {
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
