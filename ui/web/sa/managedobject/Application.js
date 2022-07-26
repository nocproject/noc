//---------------------------------------------------------------------
// sa.managedobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.Application");

Ext.define("NOC.sa.managedobject.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.RepoPreview",
        "NOC.core.combotree.ComboTree",
        "NOC.core.TagsField",
        "NOC.core.tagfield.Tagfield",
        "NOC.core.label.LabelField",
        "NOC.core.label.LabelDisplay",
        "NOC.core.PasswordField",
        "NOC.sa.administrativedomain.TreeCombo",
        "NOC.sa.administrativedomain.LookupField",
        "NOC.sa.authprofile.LookupField",
        "NOC.sa.managedobject.Model",
        "NOC.sa.managedobject.AttributesModel",
        "NOC.sa.managedobject.CapabilitiesModel",
        "NOC.sa.managedobject.LookupField",
        "NOC.sa.managedobject.SchemeLookupField",
        "NOC.sa.profile.LookupField",
        "NOC.sa.managedobjectprofile.LookupField",
        "NOC.sa.managedobject.ConfDBPanel",
        "NOC.sa.managedobject.ConsolePanel",
        "NOC.sa.managedobject.InventoryPanel",
        "NOC.sa.managedobject.InterfacePanel",
        "NOC.sa.managedobject.SensorsPanel",
        "NOC.sa.managedobject.CPEPanel",
        "NOC.sa.managedobject.ScriptPanel",
        "NOC.sa.managedobject.LinksPanel",
        "NOC.sa.managedobject.DiscoveryPanel",
        "NOC.sa.managedobject.AlarmPanel",
        "NOC.sa.managedobject.InteractionsPanel",
        "NOC.sa.managedobject.CapsPanel",
        "NOC.sa.managedobject.RepoPreview",
        "NOC.main.pool.LookupField",
        "NOC.main.ref.stencil.LookupField",
        "NOC.main.timepattern.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.main.handler.LookupField",
        "NOC.project.project.LookupField",
        "NOC.inv.vendor.LookupField",
        "NOC.inv.platform.LookupField",
        "NOC.inv.firmware.LookupField",
        "NOC.inv.resourcegroup.LookupField",
        "NOC.inv.platform.LookupField",
        "NOC.inv.map.Maintenance",
        "NOC.inv.networksegment.TreeCombo",
        "NOC.vc.vcdomain.LookupField",
        "NOC.vc.l2domain.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.fm.ttsystem.LookupField",
        "NOC.maintenance.maintenancetype.LookupField",
        "NOC.main.glyph.LookupField",
        "NOC.main.ref.soposition.LookupField",
        "NOC.main.ref.soform.LookupField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.sa.managedobject.Model",
    search: true,
    helpId: "reference-managed-object",
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
        },
        {
            title: __("New Maintaince"),
            glyph: NOC.glyph.wrench,
            run: "newMaintaince"
        },
        {
            title: __("Add to Maintaince"),
            glyph: NOC.glyph.plus,
            run: "addToMaintaince"
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

        me.configPreviewButton = Ext.create("Ext.button.Button", {
            text: __("Config"),
            glyph: NOC.glyph.file,
            scope: me,
            handler: me.onConfig
        });

        me.confdbPreviewButton = Ext.create("Ext.button.Button", {
            text: __("ConfDB"),
            glyph: NOC.glyph.file_code_o,
            scope: me,
            handler: me.onConfDB
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

        me.sensorsButton = Ext.create("Ext.button.Button", {
            text: __("Sensors"),
            glyph: NOC.glyph.thermometer_full,
            scope: me,
            handler: me.onSensors
        });

        me.cpeButton = Ext.create("Ext.button.Button", {
            text: __("CPE"),
            glyph: NOC.glyph.share_alt,
            scope: me,
            handler: me.onCPE
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

        me.ITEM_CONFIG = me.registerItem(
            Ext.create("NOC.sa.managedobject.RepoPreview", {
                app: me,
                previewName: "{0} config",
                restUrl: "/sa/managedobject/{0}/repo/cfg/",
                historyHashPrefix: "config"
            })
        );
        me.ITEM_CONFDB = me.registerItem("NOC.sa.managedobject.ConfDBPanel");
        me.ITEM_CONSOLE = me.registerItem(
            Ext.create("NOC.sa.managedobject.ConsolePanel", {app: me})
        );
        me.ITEM_INVENTORY = me.registerItem("NOC.sa.managedobject.InventoryPanel");
        me.ITEM_INTERFACE = me.registerItem("NOC.sa.managedobject.InterfacePanel");
        me.ITEM_SENSORS = me.registerItem("NOC.sa.managedobject.SensorsPanel");
        me.ITEM_CPE = me.registerItem("NOC.sa.managedobject.CPEPanel");
        me.ITEM_SCRIPTS = me.registerItem("NOC.sa.managedobject.ScriptPanel");
        me.ITEM_LINKS = me.registerItem("NOC.sa.managedobject.LinksPanel");

        me.ITEM_DISCOVERY = me.registerItem(
            Ext.create("NOC.sa.managedobject.DiscoveryPanel", {app: me})
        );

        me.ITEM_ALARM = me.registerItem("NOC.sa.managedobject.AlarmPanel");
        me.ITEM_INTERACTIONS = me.registerItem("NOC.sa.managedobject.InteractionsPanel");

        me.ITEM_CAPS = me.registerItem("NOC.sa.managedobject.CapsPanel");

        Ext.apply(me, {
            columns: [
                {
                    text: __("S"),
                    dataIndex: "oper_state",
                    sortable: false,
                    width: 30,
                    renderer: function(value, metaData) {
                        var color = "grey";
                        metaData.tdAttr = "data-qtip='<table style=\"font-size: 11px;\">" +
                            "<tr><td style=\"padding-right: 10px;\"><div class=\"noc-object-oper-state\" style=\"background-color: grey;\"></div></td><td>" + __("Unmanaged or ping is disabled") + "</td></tr>" +
                            "<tr><td><div class=\"noc-object-oper-state\" style=\"background-color: red;\"></div></td><td>" + __("Ping fail") + "</td></tr>" +
                            "<tr><td><div class=\"noc-object-oper-state\" style=\"background-color: yellow;\"></div></td><td>" + __("Device has alarm") + "</td></tr>" +
                            "<tr><td><div class=\"noc-object-oper-state\" style=\"background-color: green;\"></div></td><td>" + __("Device is normal") + "</td></tr>" +
                            "</table>'";
                        if(value === "failed") {
                            color = "red";
                        } else if(value === "degraded") {
                            color = "yellow";
                        } else if(value === "full") {
                            color = "green";
                        }
                        return "<div class='noc-object-oper-state' style='background-color: " + color + "'></div>";
                    }
                },
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
                    text: __("Labels"),
                    dataIndex: "labels",
                    renderer: NOC.render.LabelField,
                    align: "right",
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
                                },
                                {
                                    name: "description",
                                    xtype: "textarea",
                                    fieldLabel: __("Description"),
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "is_managed",
                                    xtype: "checkboxfield",
                                    fieldLabel: __("Is Managed?"),
                                    allowBlank: true,
                                    groupEdit: true
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
                                },
                                {
                                    name: "labels",
                                    fieldLabel: __("Labels"),
                                    xtype: "labelfield",
                                    allowBlank: true,
                                    query: {
                                        "enable_managedobject": true
                                    }
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Effective Labels"),
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
                                    name: "effective_labels",
                                    xtype: "labeldisplay",
                                    fieldLabel: __("Effective"),
                                    allowBlank: true,
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
                                    tooltip: __(
                                        "More settings for worked with devices. <br/>" +
                                        "Place on Service Activaton -> Setup -> Object Profile."
                                    ),
                                    itemId: "object_profile",
                                    allowBlank: false,
                                    tabIndex: 20,
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
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
                                },
                                {
                                    name: "shape_overlay_glyph",
                                    xtype: "main.glyph.LookupField",
                                    fieldLabel: __("Glyph"),
                                    allowBlank: true
                                },
                                {
                                    name: "shape_overlay_position",
                                    xtype: "main.ref.soposition.LookupField",
                                    fieldLabel: __("Position"),
                                    allowBlank: true
                                },
                                {
                                    name: "shape_overlay_form",
                                    xtype: "main.ref.soform.LookupField",
                                    fieldLabel: __("Form"),
                                    allowBlank: true
                                }
                            ]
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
                                    tooltip: __(
                                        "Profile (Adapter) for device work. <br/>" +
                                        "!! Auto detect profile by SNMP if Object Profile -> Box -> Profile is set. <br/>"
                                    ),
                                    allowBlank: false,
                                    tabIndex: 30,
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                }, {
                                    name: "vendor",
                                    xtype: "inv.vendor.LookupField",
                                    fieldLabel: __("Vendor"),
                                    tooltip: __(
                                        "Set after Version Discovery. Not for manual set"
                                    ),
                                    allowBlank: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                }, {
                                    name: "platform",
                                    xtype: "inv.platform.LookupField",
                                    fieldLabel: __("Platform"),
                                    tooltip: __(
                                        "Set after Version Discovery. Not for manual set"
                                    ),
                                    allowBlank: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                }
                            ]
                        }, {
                            xtype: "container",
                            items: [
                                {
                                    name: "version",
                                    xtype: "inv.firmware.LookupField",
                                    fieldLabel: __("Version"),
                                    allowBlank: true
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
                                    groupEdit: true
                                },
                                {
                                    name: "address",
                                    xtype: "textfield",
                                    fieldLabel: __("Address"),
                                    allowBlank: false,
                                    tabIndex: 50,
                                    groupEdit: true,
                                    vtype: "IPv4"
                                },
                                {
                                    name: "access_preference",
                                    xtype: "combobox",
                                    fieldLabel: __("Access Preference"),
                                    tooltip: __(
                                        "Preference mode with worked profile script. <br/>" +
                                        "!! Work if Device Profile supported. <br/>" +
                                        "Profile (default) - use Object Profile settings <br/>" +
                                        "S - Use only SNMP when access to device" +
                                        "CLI Only - Use only CLI when access to device" +
                                        "SNMP, CLI - Use SNMP, if not avail swithc to CLI" +
                                        "CLI, SNMP - Use CLI, if not avail swithc to SNMP"
                                    ),
                                    allowBlank: true,
                                    store: [
                                        ["P", __("Profile")],
                                        ["S", __("SNMP Only")],
                                        ["C", __("CLI Only")],
                                        ["SC", __("SNMP, CLI")],
                                        ["CS", __("CLI, SNMP")]
                                    ],
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "port",
                                    xtype: "numberfield",
                                    fieldLabel: __("Port"),
                                    allowBlank: true,
                                    minValue: 0,
                                    maxValue: 65535,
                                    hideTrigger: true,
                                    groupEdit: true

                                },
                                {
                                    name: "cli_session_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("CLI Session Policy"),
                                    tooltip: __(
                                        "Use one session worked on device. <br/>" +
                                        "Profile (default) - use Object Profile settings <br/>" +
                                        "Enable - login when statr job, logout after end." +
                                        "Disable - worked one script - one login. Logout after script end."),
                                    allowBlank: true,
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "cli_privilege_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("CLI Privilege Policy"),
                                    tooltip: __(
                                        "Do enable if login unprivilege mode on device. <br/>" +
                                        "Raise Privileges - send enable<br/>" +
                                        "Do not raise - work on current mode (immediately after login)"
                                    ),
                                    allowBlank: true,
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Raise Privileges")],
                                        ["D", __("Don't Raise")]
                                    ],
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "remote_path",
                                    xtype: "textfield",
                                    fieldLabel: __("Path"),
                                    allowBlank: true,
                                    groupEdit: true
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
                                    tooltip: __(
                                        'Get credentials (user, pass, snmp etc.) from Auth profile.<br/> ' +
                                        ' Service Activation -> Setup -> Auth Profile. If set - ' +
                                        'value in field user, password, snmp community will be IGNORED'
                                    ),
                                    tabIndex: 60,
                                    allowBlank: true,
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "user",
                                    xtype: "textfield",
                                    fieldLabel: __("User"),
                                    tabIndex: 61,
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "password",
                                    xtype: "password",
                                    fieldLabel: __("Password"),
                                    tabIndex: 62,
                                    allowBlank: true,
                                    inputType: "password",
                                    groupEdit: true
                                },
                                {
                                    name: "super_password",
                                    xtype: "password",
                                    fieldLabel: __("Super Password"),
                                    allowBlank: true,
                                    inputType: "password",
                                    groupEdit: true
                                },
                                {
                                    name: "snmp_ro",
                                    xtype: "password",
                                    fieldLabel: __("RO Community"),
                                    tabIndex: 63,
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "snmp_rw",
                                    xtype: "password",
                                    fieldLabel: __("RW Community"),
                                    tabIndex: 64,
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "max_scripts",
                                    xtype: "numberfield",
                                    fieldLabel: __("Max. Scripts"),
                                    allowBlank: true,
                                    hideTrigger: true,
                                    minValue: 0,
                                    maxValue: 99,
                                    groupEdit: true
                                },
                                {
                                    name: "snmp_rate_limit",
                                    xtype: "numberfield",
                                    fieldLabel: __("SNMP Rate limit"),
                                    tooltip: __(
                                        'Limit SNMP (Query per second).'
                                    ),
                                    allowBlank: true,
                                    hideTrigger: true,
                                    minValue: 0,
                                    maxValue: 99,
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "time_pattern",
                                    xtype: "main.timepattern.LookupField",
                                    fieldLabel: __("Time Pattern"),
                                    tooltip: __(
                                        'Use this field if you want disable ping check on specified time.<br/> ' +
                                        ' Main -> Setup -> Time Patterns'
                                    ),
                                    allowBlank: true,
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
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
                                    tooltip: __(
                                        "Use for setup User permission on Object. <br/>" +
                                        "Place on Service Activaton -> Setup -> Administrative Domain.<br/>" +
                                        "Permission on Activaton -> Setup -> Group Access/User Access.<br/>"
                                    ),
                                    allowBlank: false,
                                    tabIndex: 90,
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }

                                },
                                {
                                    name: "segment",
                                    xtype: "noc.core.combotree",
                                    restUrl: "/inv/networksegment/",
                                    fieldLabel: __("Segment"),
                                    allowBlank: false,
                                    tabIndex: 100,
                                    groupEdit: true
                                },
                                {
                                    name: "pool",
                                    xtype: "main.pool.LookupField",
                                    fieldLabel: __("Pool"),
                                    tooltip: __(
                                        "Use for shard devices over intersection IP Address spaces. <br/>" +
                                        "Create and Set on Tower<br/>"
                                    ),
                                    allowBlank: false,
                                    tabIndex: 110,
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "project",
                                    xtype: "project.project.LookupField",
                                    fieldLabel: __("Project"),
                                    allowBlank: true,
                                    tabIndex: 111,
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "fqdn",
                                    xtype: "textfield",
                                    fieldLabel: __("FQDN"),
                                    tooltip: __(
                                        "Set device name. If FQDN suffix is not set use dot after name: NAME.<br/>" +
                                        "FQND suffix set on Object Profile: " +
                                        "Service Activation -> Setup -> Object Profile -> Common<br/>"
                                    ),
                                    allowBlank: true,
                                    uiStyle: "medium",
                                    tabIndex: 120,
                                    listeners: {
                                        render: me.addTooltip
                                    }
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
                                    name: "l2_domain",
                                    xtype: "vc.l2domain.LookupField",
                                    fieldLabel: __("L2 Domain"),
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
                                    ]
                                },
                                {
                                    name: "address_resolution_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Address Resolution Policy"),
                                    tooltip: __(
                                        'Activate resolve Address by FQND field (or other handler).<br/> ' +
                                        'Profile - Use profile settings<br/>' +
                                        'Disable - Do not resolve FQDN into Address field<br/>' +
                                        'Once - Once resolve FQDN (after success settings will be set to Disable)<br/>' +
                                        'Enable - Enable resolve address before running Job<br/>'
                                    ),
                                    store: [
                                        ["P", __("Profile")],
                                        ["D", __("Disabled")],
                                        ["O", __("Once")],
                                        ["E", __("Enabled")]
                                    ],
                                    allowBlank: false,
                                    uiStyle: "medium",
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Discovery"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            name: "config_policy",
                            xtype: "combobox",
                            reference: "configPolicy",
                            fieldLabel: __("Config Policy"),
                            allowBlank: false,
                            tooltip: __('Select method of config gathering'),
                            displayField: "label",
                            valueField: "id",
                            store: {
                                fields: ["id", "label"],
                                data: [
                                    {"id": "P", "label": __("Profile")},
                                    {"id": "s", "label": __("Script")},
                                    {"id": "S", "label": __("Script, Download")},
                                    {"id": "D", "label": __("Download, Script")},
                                    {"id": "d", "label": __("Download")}
                                ]
                            }
                        },
                        {
                            name: "config_fetch_policy",
                            xtype: "combobox",
                            fieldLabel: __("Config fetch Policy"),
                            allowBlank: false,
                            tooltip: __('Select method of config fetching'),
                            displayField: "label",
                            valueField: "id",
                            store: {
                                fields: ["id", "label"],
                                data: [
                                    {"id": "P", "label": __("Profile")},
                                    {"id": "s", "label": __("Prefer Startup")},
                                    {"id": "r", "label": __("Prefer Running")}
                                ]
                            }
                        },
                        {
                            name: "caps_discovery_policy",
                            xtype: "combobox",
                            fieldLabel: __("Caps Policy"),
                            store: [
                                ["P", __("Profile")],
                                ["s", __("Script")],
                                ["S", __("Script, ConfDB")],
                                ["C", __("ConfDB, Script")],
                                ["c", __("ConfDB")]
                            ],
                            allowBlank: false,
                            uiStyle: "medium"
                        },
                        {
                            name: "interface_discovery_policy",
                            xtype: "combobox",
                            fieldLabel: __("Interface Policy"),
                            store: [
                                ["P", __("Profile")],
                                ["s", __("Script")],
                                ["S", __("Script, ConfDB")],
                                ["C", __("ConfDB, Script")],
                                ["c", __("ConfDB")]
                            ],
                            allowBlank: false,
                            uiStyle: "medium"
                        },
                        {
                            name: "vlan_discovery_policy",
                            xtype: "combobox",
                            fieldLabel: __("VLAN Policy"),
                            store: [
                                ["P", __("Profile")],
                                ["s", __("Script")],
                                ["S", __("Script, ConfDB")],
                                ["C", __("ConfDB, Script")],
                                ["c", __("ConfDB")]
                            ],
                            allowBlank: false,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("ConfDB"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            name: "confdb_raw_policy",
                            xtype: "combobox",
                            fieldLabel: __("Raw Policy"),
                            store: [
                                ["P", __("Profile")],
                                ["E", __("Enable")],
                                ["D", __("Disable")]
                            ],
                            allowBlank: false,
                            groupEdit: true
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
                                    name: "fm_pool",
                                    xtype: "main.pool.LookupField",
                                    fieldLabel: __("FM Pool"),
                                    tooltip: __(
                                        "Use to override pool for events processing"
                                    ),
                                    allowBlank: true,
                                    tabIndex: 130,
                                    groupEdit: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "event_processing_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Event Policy"),
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    allowBlank: false,
                                    groupEdit: true
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
                                    listeners: {
                                        scope: me,
                                        change: function(combo, newValue) {
                                            combo.nextSibling().setHidden(newValue !== "s");
                                        },
                                        afterrender: function(combo) {
                                            combo.nextSibling().setHidden(combo.value !== "s");
                                        }
                                    },
                                    groupEdit: true
                                },
                                {
                                    name: "trap_source_ip",
                                    xtype: "textfield",
                                    fieldLabel: __("Trap Source IP"),
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "syslog_archive_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Syslog Archive Policy"),
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    allowBlank: false,
                                    groupEdit: true
                                }
                            ]
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
                                    listeners: {
                                        scope: me,
                                        change: function(combo, newValue) {
                                            combo.nextSibling().setHidden(newValue !== "s");
                                        },
                                        afterrender: function(combo) {
                                            combo.nextSibling().setHidden(combo.value !== "s");
                                        }
                                    },
                                    groupEdit: true
                                },
                                {
                                    name: "syslog_source_ip",
                                    xtype: "textfield",
                                    fieldLabel: __("Syslog Source IP"),
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "trap_community",
                                    xtype: "password",
                                    fieldLabel: __("Trap Community"),
                                    allowBlank: true,
                                    groupEdit: true
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Resource Groups"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    collapsed: false,
                    items: [
                        {
                            name: "static_service_groups",
                            xtype: "gridfield",
                            columns: [
                                // {
                                //     xtype: "glyphactioncolumn",
                                //     width: 20,
                                //     sortable: false,
                                //     items: [
                                //         {
                                //             glyph: NOC.glyph.search,
                                //             tooltip: __("Show Card"),
                                //             scope: me,
                                //             handler: me.onShowResourceGroup
                                //         }
                                //     ]
                                // },
                                {
                                    dataIndex: "group",
                                    text: __("Static Service Groups"),
                                    width: 350,
                                    renderer: NOC.render.Lookup("group"),
                                    editor: {
                                        xtype: "inv.resourcegroup.LookupField"
                                    }
                                }
                            ]
                        },
                        {
                            name: "effective_service_groups",
                            xtype: "gridfield",
                            columns: [
                                {
                                    dataIndex: "group",
                                    text: __("Effective Service Groups"),
                                    width: 350,
                                    renderer: NOC.render.Lookup("group"),
                                    editor: {
                                        xtype: "inv.resourcegroup.LookupField"
                                    }
                                }
                            ]
                        },
                        {
                            name: "static_client_groups",
                            xtype: "gridfield",
                            columns: [
                                {
                                    dataIndex: "group",
                                    text: __("Static Client Groups"),
                                    width: 350,
                                    renderer: NOC.render.Lookup("group"),
                                    editor: {
                                        xtype: "inv.resourcegroup.LookupField"
                                    }
                                }
                            ]
                        },
                        {
                            name: "effective_client_groups",
                            xtype: "gridfield",
                            columns: [
                                {
                                    dataIndex: "group",
                                    text: __("Effective Client Groups"),
                                    width: 350,
                                    renderer: NOC.render.Lookup("group"),
                                    editor: {
                                        xtype: "inv.resourcegroup.LookupField"
                                    }
                                }
                            ]
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
                                    name: "config_filter_handler",
                                    xtype: "main.handler.LookupField",
                                    fieldLabel: __("Config Filter Handler"),
                                    allowBlank: true,
                                    groupEdit: true,
                                    query: {
                                        allow_config_filter: true
                                    }
                                },
                                {
                                    name: "config_diff_filter_handler",
                                    xtype: "main.handler.LookupField",
                                    fieldLabel: __("Config Diff Filter Handler"),
                                    allowBlank: true,
                                    groupEdit: true,
                                    query: {
                                        allow_config_filter: true
                                    }
                                }]
                        }, {
                            xtype: "container",
                            items: [
                                {
                                    name: "config_validation_handler",
                                    xtype: "main.handler.LookupField",
                                    fieldLabel: __("Config Validation Handler"),
                                    allowBlank: true,
                                    groupEdit: true,
                                    query: {
                                        allow_config_validation: true
                                    }
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
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")],
                                        ["R", __("As Depended")]
                                    ],
                                    groupEdit: true
                                },
                                {
                                    name: "tt_system",
                                    xtype: "fm.ttsystem.LookupField",
                                    fieldLabel: __("TT System"),
                                    allowBlank: true,
                                    groupEdit: true
                                }]
                        }, {
                            xtype: "container",
                            items: [
                                {
                                    name: "tt_queue",
                                    xtype: "textfield",
                                    fieldLabel: __("TT Queue"),
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "tt_system_id",
                                    xtype: "textfield",
                                    fieldLabel: __("TT System ID"),
                                    allowBlank: true
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
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    groupEdit: true
                                }]
                        },
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "periodic_discovery_alarm_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Periodic Alarm"),
                                    allowBlank: true,
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    groupEdit: true
                                }]
                        },
                        {
                            xtype: "container",
                            items: [
                                {
                                    name: "denied_firmware_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("On Denied Firmware"),
                                    allowBlank: true,
                                    store: [
                                        ["P", __("Profile")],
                                        ["I", __("Ignore")],
                                        ["s", __("Ignore&Stop")],
                                        ["A", __("Raise Alarm")],
                                        ["S", __("Raise Alarm&Stop")]
                                    ],
                                    groupEdit: true
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
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    groupEdit: true
                                },
                                {
                                    name: "box_discovery_telemetry_sample",
                                    xtype: "numberfield",
                                    fieldLabel: __("Box Sample"),
                                    groupEdit: true
                                }]
                        }, {
                            xtype: "container",
                            items: [
                                {
                                    name: "periodic_discovery_telemetry_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Periodic Telemetry"),
                                    allowBlank: true,
                                    store: [
                                        ["P", __("Profile")],
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    groupEdit: true
                                },
                                {
                                    name: "periodic_discovery_telemetry_sample",
                                    xtype: "numberfield",
                                    fieldLabel: __("Periodic Sample"),
                                    groupEdit: true
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
                me.confdbPreviewButton,
                me.inventoryButton,
                me.interfacesButton,
                me.sensorsButton,
                me.cpeButton,
                me.linksButton,
                me.discoveryButton,
                me.alarmsButton,
                me.maintainceButton,
                me.interactionsButton,
                me.validationSettingsButton,
                me.capsButton
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
            title: __("By Geo Address"),
            ftype: "geoaddress",
            hidden: !NOC.settings.has_geocoder
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
            title: __("By Service Group (Selector)"),
            name: "effective_service_groups",
            ftype: "tree",
            lookup: "inv.resourcegroup"
        },
        {
            title: __("By Client Group"),
            name: "effective_client_groups",
            ftype: "tree",
            lookup: "inv.resourcegroup"
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
            title: __("By L2 Domain"),
            name: "l2_domain",
            ftype: "lookup",
            lookup: "vc.l2domain"
        },
        {
            title: __("By Controller"),
            name: "controller",
            ftype: "lookup",
            lookup: "sa.managedobject"
        },
        {
            title: __("Platform"),
            name: "platform",
            ftype: "lookup",
            lookup: "inv.platform"
        },
        {
            title: __("By Labels"),
            name: "labels",
            ftype: "label",
            filterProtected: false
        }
    ],
    inlines:
        [
            {
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
            },
            {
                title: __("Capabilities"),
                collapsed: false,
                model: "NOC.sa.managedobject.CapabilitiesModel",
                columns: [
                    {
                        text: __("Capability"),
                        dataIndex: "capability",
                        width: 300
                    },
                    {
                        text: __("Value"),
                        dataIndex: "value",
                        width: 100,
                        renderer: function(v) {
                            if((v === true) || (v === false)) {
                                return NOC.render.Bool(v);
                            } else {
                                return v;
                            }
                        }
                    },
                    {
                        text: __("Scope"),
                        dataIndex: "scope",
                        width: 50
                    },
                    {
                        text: __("Source"),
                        dataIndex: "source",
                        width: 100
                    },
                    {
                        text: __("Description"),
                        dataIndex: "description",
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
            args: [me.currentRecord.get("segment"), me.currentRecord.get("id")]
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
    onConfDB: function() {
        var me = this;
        me.previewItem(me.ITEM_CONFDB, me.currentRecord);
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
    onSensors: function() {
        var me = this;
        me.previewItem(me.ITEM_SENSORS, me.currentRecord);
    },
    //
    onCPE: function() {
        var me = this;
        me.previewItem(me.ITEM_CPE, me.currentRecord);
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
            contacts: NOC.email ? NOC.email : NOC.username,
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
        me.configPreviewButton.setDisabled(disabled || !me.hasPermission("config"));
        me.confdbPreviewButton.setDisabled(disabled || !me.hasPermission("config"));
        me.consoleButton.setDisabled(disabled || !me.hasPermission("console") || !me.currentRecord.get("is_managed"));
        me.scriptsButton.setDisabled(disabled || !me.hasPermission("script") || !me.currentRecord.get("is_managed"));
        me.interfacesButton.setDisabled(disabled);
        me.sensorsButton.setDisabled(disabled);
        me.cpeButton.setDisabled(disabled);
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
                case "interfaces":
                    me.onInterfaces();
                    break;
                case "sensors":
                    me.onSensors();
                    break;
                case "links":
                    me.onLinks();
                    break;
            }
        });
    },
    // Show ResourceGroup card
    onShowResourceGroup: function(grid, rowIndex) {
        var me = this,
            r = me.store.getAt(rowIndex),
            id = r.get("group");
        window.open("/api/card/view/resourcegroup/" + id + "/", "_blank");
    }
});
