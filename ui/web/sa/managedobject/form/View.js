//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
fieldSetDefaults = {
    xtype: "container",
    padding: 10,
    layout: "form",
    columnWidth: 0.5
};

console.debug('Defining NOC.sa.managedobject.form.View');
Ext.define('NOC.sa.managedobject.form.View', {
    extend: 'Ext.panel.Panel',
    mixins: [
        'NOC.core.ModelApplication'
    ],
    requires: [
        'NOC.core.label.LabelField',
        'NOC.core.label.LabelDisplay',
        'NOC.core.status.StatusField',
        'NOC.core.combotree.ComboTree',
        'NOC.core.ComboBox',
        'NOC.core.InlineGrid',
        'NOC.core.InlineModelStore',
        'NOC.core.StateField',
        'NOC.sa.managedobject.AttributesModel',
        'NOC.sa.managedobject.CapabilitiesModel',
        'NOC.sa.managedobject.form.FormController',
        'NOC.sa.managedobject.SchemeLookupField',
        'NOC.sa.managedobject.RepoPreview',
        'NOC.sa.managedobject.ConfDBPanel',
        'NOC.sa.managedobject.ConsolePanel',
        'NOC.sa.managedobject.ScriptPanel',
        'NOC.sa.managedobject.LinksPanel',
        'NOC.sa.managedobject.InterfacePanel',
        'NOC.sa.managedobject.SensorsPanel',
        'NOC.sa.managedobject.DiscoveryPanel',
        'NOC.sa.managedobject.AlarmPanel',
        'NOC.sa.managedobject.InventoryPanel',
        'NOC.sa.managedobject.InteractionsPanel',
    ],
    alias: 'widget.managedobject.form',
    controller: 'managedobject.form',
    region: 'center',
    layout: 'card',
    border: true,
    padding: 4,
    defaults: {
        layout: 'fit'
    },
    items: [
        {
            activeItem: 0,
            itemId: 'managedobject-form-panel',
            xtype: 'form',
            layout: 'anchor',
            border: true,
            padding: 4,
            defaults: {
                anchor: "100%",
                minWidth: 800,
                maxWidth: 1000,
            },
            scrollable: true,
            listeners: {
                scope: this,
                validitychange: function(me, isValid) {
                    Ext.each(Ext.ComponentQuery.query("[itemId$=aveBtn]"), function(button) {button.setDisabled(!isValid)});
                }
            },
            items: [
                {
                    xtype: "container",
                    html: "Title",
                    itemId: "formTitle",
                    padding: 4,
                    style: {
                        fontWeight: "bold"
                    }
                },
                {
                    xtype: "fieldset",
                    layout: "column",
                    defaults: this.fieldSetDefaults,
                    border: false,
                    items: [
                        {
                            border: false,
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
                                    tabIndex: 20,
                                    groupEdit: true
                                },
                                {
                                    name: "is_managed",
                                    xtype: "checkboxfield",
                                    fieldLabel: __("Is Managed?"),
                                    readOnly: true,
                                    tabIndex: 30,
                                },
                                {
                                    name: "state",
                                    xtype: "statefield",
                                    fieldLabel: __("State"),
                                    restUrl: "sa/managedobject/",
                                    allowBlank: false
                                },
                                {
                                    name: "bi_id",
                                    xtype: "displayfield",
                                    fieldLabel: __("BI ID"),
                                    allowBlank: true
                                }
                            ]
                        }, {
                            border: false,
                            items: [ // second column
                                {
                                    name: "diagnostics",
                                    fieldLabel: __("Diag"),
                                    xtype: "statusfield",
                                    allowBlank: true,
                                },
                                {
                                    name: "labels",
                                    fieldLabel: __("Labels"),
                                    xtype: "labelfield",
                                    allowBlank: true,
                                    minWidth: 100,
                                    tabIndex: 40,
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
                    defaults: this.fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            items: [
                                {
                                    name: "object_profile",
                                    xtype: "core.combo",
                                    restUrl: "/sa/managedobjectprofile/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Object Profile"),
                                    tooltip: __(
                                        "More settings for worked with devices. <br/>" +
                                        "Place on Service Activaton -> Setup -> Object Profile."
                                    ),
                                    itemId: "object_profile",
                                    allowBlank: false,
                                    tabIndex: 50,
                                    groupEdit: true,
                                    listeners: {
                                        render: 'addTooltip'
                                    }
                                }
                            ]
                        },
                        {
                            items: [
                                {
                                    name: "shape",
                                    xtype: "core.combo",
                                    restUrl: "/main/ref/stencil/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Shape"),
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "shape_overlay_glyph",
                                    xtype: "core.combo",
                                    restUrl: "/main/glyph/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Glyph"),
                                    allowBlank: true
                                },
                                {
                                    name: "shape_overlay_position",
                                    xtype: "core.combo",
                                    restUrl: "/main/ref/soposition/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Position"),
                                    allowBlank: true
                                },
                                {
                                    name: "shape_overlay_form",
                                    xtype: "core.combo",
                                    restUrl: "/main/ref/soform/lookup/",
                                    uiStyle: "medium-combo",
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
                    defaults: this.fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            items: [
                                {
                                    name: "profile",
                                    xtype: "core.combo",
                                    restUrl: "/sa/profile/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("SA Profile"),
                                    tooltip: __(
                                        "Profile (Adapter) for device work. <br/>" +
                                        "!! Auto detect profile by SNMP if Object Profile -> Box -> Profile is set. <br/>"
                                    ),
                                    allowBlank: true,
                                    tabIndex: 60,
                                    groupEdit: true,
                                    listeners: {
                                        render: 'addTooltip'
                                    }
                                }, {
                                    name: "vendor",
                                    xtype: "core.combo",
                                    restUrl: "/inv/vendor/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Vendor"),
                                    tooltip: __(
                                        "Set after Version Discovery. Not for manual set"
                                    ),
                                    allowBlank: true,
                                    listeners: {
                                        render: 'addTooltip'
                                    }
                                }, {
                                    name: "platform",
                                    xtype: "core.combo",
                                    restUrl: "/inv/platform/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Platform"),
                                    tooltip: __(
                                        "Set after Version Discovery. Not for manual set"
                                    ),
                                    allowBlank: true,
                                    listeners: {
                                        render: 'addTooltip'
                                    }
                                }
                            ]
                        }, {
                            items: [
                                {
                                    name: "version",
                                    xtype: "core.combo",
                                    restUrl: "/inv/firmware/lookup/",
                                    uiStyle: "medium-combo",
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
                    defaults: this.fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            items: [
                                {
                                    name: "scheme",
                                    xtype: "sa.managedobject.SchemeLookupField",
                                    fieldLabel: __("Scheme"),
                                    allowBlank: false,
                                    tabIndex: 70,
                                    groupEdit: true
                                },
                                {
                                    name: "address",
                                    xtype: "textfield",
                                    fieldLabel: __("Address"),
                                    allowBlank: false,
                                    tabIndex: 80,
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
                                        render: 'addTooltip'
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
                                        render: 'addTooltip'
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
                                        render: 'addTooltip'
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
                            items: [
                                {
                                    name: "auth_profile",
                                    xtype: "core.combo",
                                    restUrl: "/sa/authprofile/lookup/",
                                    uiStyle: "medium-combo",
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
                                        render: 'addTooltip'
                                    }
                                },
                                {
                                    name: "user",
                                    xtype: "textfield",
                                    fieldLabel: __("User"),
                                    tabIndex: 70,
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "password",
                                    xtype: "password",
                                    fieldLabel: __("Password"),
                                    tabIndex: 80,
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
                                    tabIndex: 90,
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "snmp_rw",
                                    xtype: "password",
                                    fieldLabel: __("RW Community"),
                                    tabIndex: 100,
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
                                        render: 'addTooltip'
                                    }
                                },
                                {
                                    name: "time_pattern",
                                    xtype: "core.combo",
                                    restUrl: "/main/timepattern/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Time Pattern"),
                                    tooltip: __(
                                        'Use this field if you want disable ping check on specified time.<br/> ' +
                                        ' Main -> Setup -> Time Patterns'
                                    ),
                                    allowBlank: true,
                                    groupEdit: true,
                                    listeners: {
                                        render: 'addTooltip'
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
                    defaults: this.fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            items: [
                                {
                                    name: "administrative_domain",
                                    xtype: "noc.core.combotree",
                                    restUrl: "/sa/administrativedomain/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Administrative Domain"),
                                    tooltip: __(
                                        "Use for setup User permission on Object. <br/>" +
                                        "Place on Service Activaton -> Setup -> Administrative Domain.<br/>" +
                                        "Permission on Activaton -> Setup -> Group Access/User Access.<br/>"
                                    ),
                                    allowBlank: false,
                                    tabIndex: 110,
                                    groupEdit: true,
                                    listeners: {
                                        render: 'addTooltip'
                                    }
                                },
                                {
                                    name: "segment",
                                    xtype: "noc.core.combotree",
                                    restUrl: "/inv/networksegment/",
                                    fieldLabel: __("Segment"),
                                    allowBlank: false,
                                    tabIndex: 120,
                                    groupEdit: true
                                },
                                {
                                    name: "pool",
                                    xtype: "core.combo",
                                    restUrl: "/main/pool/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Pool"),
                                    tooltip: __(
                                        "Use for shard devices over intersection IP Address spaces. <br/>" +
                                        "Create and Set on Tower<br/>"
                                    ),
                                    allowBlank: false,
                                    tabIndex: 130,
                                    groupEdit: true,
                                    listeners: {
                                        render: 'addTooltip'
                                    }
                                },
                                {
                                    name: "project",
                                    xtype: "core.combo",
                                    restUrl: "/project/project/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Project"),
                                    allowBlank: true,
                                    tabIndex: 140,
                                    groupEdit: true,
                                    listeners: {
                                        render: 'addTooltip'
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
                                    tabIndex: 150,
                                    listeners: {
                                        render: 'addTooltip'
                                    }
                                }
                            ]
                        }, {
                            items: [
                                {
                                    name: "vrf",
                                    xtype: "core.combo",
                                    restUrl: "/ip/vrf/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("VRF"),
                                    allowBlank: true,
                                    groupEdit: true
                                },
                                {
                                    name: "l2_domain",
                                    xtype: "core.combo",
                                    restUrl: "/vc/l2domain/lookup/",
                                    uiStyle: "medium-combo",
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
                                        render: 'addTooltip'
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
                    defaults: this.fieldSetDefaults,
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
                    defaults: this.fieldSetDefaults,
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
                    defaults: this.fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            items: [
                                {
                                    name: "fm_pool",
                                    xtype: "core.combo",
                                    restUrl: "/main/pool/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("FM Pool"),
                                    tooltip: __(
                                        "Use to override pool for events processing"
                                    ),
                                    allowBlank: true,
                                    tabIndex: 160,
                                    groupEdit: true,
                                    listeners: {
                                        render: 'addTooltip'
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
                                        scope: this,
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
                                        scope: this,
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
                    defaults: this.fieldSetDefaults,
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
                                //             scope: this,
                                //             handler: this.onShowResourceGroup
                                //         }
                                //     ]
                                // },
                                {
                                    dataIndex: "group",
                                    text: __("Static Service Groups"),
                                    width: 350,
                                    renderer: NOC.render.Lookup("group"),
                                    editor: {
                                        xtype: "core.combo",
                                        restUrl: "/inv/resourcegroup/lookup/",

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
                                        xtype: "core.combo",
                                        restUrl: "/inv/resourcegroup/lookup/",
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
                                        xtype: "core.combo",
                                        restUrl: "/inv/resourcegroup/lookup/",
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
                                        xtype: "core.combo",
                                        restUrl: "/inv/resourcegroup/lookup/",
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
                    defaults: this.fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
                            items: [
                                {
                                    name: "controller",
                                    xtype: "core.combo",
                                    restUrl: "/sa/managedobject/lookup/",
                                    uiStyle: "medium-combo",
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
                    defaults: this.fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
                            items: [
                                {
                                    name: "config_filter_handler",
                                    xtype: "core.combo",
                                    restUrl: "/main/handler/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Config Filter Handler"),
                                    allowBlank: true,
                                    groupEdit: true,
                                    query: {
                                        allow_config_filter: true
                                    }
                                },
                                {
                                    name: "config_diff_filter_handler",
                                    xtype: "core.combo",
                                    restUrl: "/main/handler/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("Config Diff Filter Handler"),
                                    allowBlank: true,
                                    groupEdit: true,
                                    query: {
                                        allow_config_filter: true
                                    }
                                }]
                        }, {
                            items: [
                                {
                                    name: "config_validation_handler",
                                    xtype: "core.combo",
                                    restUrl: "/main/handler/lookup/",
                                    uiStyle: "medium-combo",
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
                    defaults: this.fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
                            items: [
                                {
                                    name: "remote_system",
                                    xtype: "core.combo",
                                    restUrl: "/main/remotesystem/lookup/",
                                    uiStyle: "medium-combo",
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
                            items: []
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Escalation"),
                    layout: "column",
                    defaults: this.fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
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
                                    xtype: "core.combo",
                                    restUrl: "/fm/ttsystem/lookup/",
                                    uiStyle: "medium-combo",
                                    fieldLabel: __("TT System"),
                                    allowBlank: true,
                                    groupEdit: true
                                }]
                        }, {
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
                    defaults: this.fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
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
                    defaults: this.fieldSetDefaults,
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
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
                },
                {
                    xtype: "fieldset",
                    anchor: "100%",
                    minHeight: 130,
                    title: __("Attributes"),
                    collapsible: true,
                    collapsed: true,
                    items: [
                        {
                            xtype: "inlinegrid",
                            itemId: "sa-managedobject-attr-inline",
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
                    ],
                },
                {
                    xtype: "fieldset",
                    anchor: "100%",
                    minHeight: 130,
                    title: __("Capabilities"),
                    collapsible: true,
                    collapsed: false,
                    items: [
                        {
                            xtype: "inlinegrid",
                            itemId: "sa-managedobject-caps-inline",
                            model: "NOC.sa.managedobject.CapabilitiesModel",
                            readOnly: true,
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
                    ]
                },
            ]
        },
        {
            activeItem: 1,
            itemId: 'sa-config',
            xtype: 'sa.repopreview',
            historyHashPrefix: "config",  // suffix from itemId
            app: this,
            previewName: "{0} config",
            restUrl: "/sa/managedobject/{0}/repo/cfg/",
            onClose: function() {
                this.up().setActiveItem(this.backItem);
                this.up('[appId=sa.managedobject]').setHistoryHash(this.currentRecord.id);
            },
        },
        {
            activeItem: 2,
            itemId: 'sa-confdb',
            xtype: 'sa.confdb',
            historyHashPrefix: "confdb",  // suffix from itemId
            app: this,
            onClose: function() {
                this.up().setActiveItem(this.backItem);
                this.up('[appId=sa.managedobject]').setHistoryHash(this.currentRecord.id);
            },
        },
        {
            activeItem: 3,
            itemId: 'sa-console',
            xtype: 'sa.console',
            historyHashPrefix: 'console', // suffix from itemId
            app: this,
            onClose: function() {
                this.up().setActiveItem(this.backItem);
                this.up('[appId=sa.managedobject]').setHistoryHash(this.currentRecord.id);
            },
        },
        {
            activeItem: 4,
            itemId: 'sa-script',
            xtype: 'sa.script',
            historyHashPrefix: 'script', // suffix from itemId
            app: this,
            onClose: function() {
                this.up().setActiveItem(this.backItem);
                this.up('[appId=sa.managedobject]').setHistoryHash(this.currentRecord.id);
            },
        },
        {
            activeItem: 5,
            itemId: 'sa-interface_count',
            xtype: 'sa.interfacepanel',
            historyHashPrefix: 'interface_count', // suffix from itemId
            app: this,
            onClose: function() {
                this.up().setActiveItem(this.backItem);
                this.up('[appId=sa.managedobject]').setHistoryHash(this.currentRecord.id);
            },
        },
        {
            activeItem: 6,
            itemId: 'sa-sensors',
            xtype: 'sa.sensors',
            historyHashPrefix: 'sensors', // suffix from itemId
            app: this,
            onClose: function() {
                this.up().setActiveItem(this.backItem);
                this.up('[appId=sa.managedobject]').setHistoryHash(this.currentRecord.id);
            },
        },
        {
            activeItem: 7,
            itemId: 'sa-link_count',
            xtype: 'sa.links',
            historyHashPrefix: 'link_count', // suffix from itemId
            app: this,
            onClose: function() {
                this.up().setActiveItem(this.backItem);
                this.up('[appId=sa.managedobject]').setHistoryHash(this.currentRecord.id);
            },
        },
        {
            activeItem: 8,
            itemId: 'sa-discovery',
            xtype: 'sa.discovery',
            historyHashPrefix: 'discovery', // suffix from itemId
            app: this,
            onClose: function() {
                this.up().setActiveItem(this.backItem);
                this.up('[appId=sa.managedobject]').setHistoryHash(this.currentRecord.id);
            },
        },
        {
            activeItem: 9,
            itemId: 'sa-alarms',
            xtype: 'sa.alarms',
            historyHashPrefix: 'alarms', // suffix from itemId
            app: this,
            onClose: function() {
                this.up().setActiveItem(this.backItem);
                this.up('[appId=sa.managedobject]').setHistoryHash(this.currentRecord.id);
            },
        },
        {
            activeItem: 10,
            itemId: 'sa-inventory',
            xtype: 'sa.inventory',
            historyHashPrefix: 'inventory', // suffix from itemId
            app: this,
            onClose: function() {
                this.up().setActiveItem(this.backItem);
                this.up('[appId=sa.managedobject]').setHistoryHash(this.currentRecord.id);
            },
        },
        {
            activeItem: 11,
            itemId: 'sa-interactions',
            xtype: 'sa.interactions',
            historyHashPrefix: 'interactions', // suffix from itemId
            app: this,
            onClose: function() {
                this.up().setActiveItem(this.backItem);
                this.up('[appId=sa.managedobject]').setHistoryHash(this.currentRecord.id);
            },
        }
    ],
    dockedItems: [{
        xtype: 'toolbar',
        dock: 'top',
        overflowHandler: "menu",
        items: [
            {
                itemId: "saveBtn",
                text: __("Save"),
                tooltip: __("Save changes"),
                glyph: NOC.glyph.save,
                handler: "onSaveRecord",
            },
            {
                itemId: "groupSaveBtn",
                text: __("Save"),
                tooltip: __("Save changes"),
                glyph: NOC.glyph.save,
                handler: "onSaveRecords",
            },
            {
                itemId: "closeBtn",
                text: __("Close"),
                tooltip: __("Close without saving"),
                glyph: NOC.glyph.arrow_left,
                handler: 'toMain'
            },
            "-",
            {
                itemId: "resetBtn",
                text: __("Reset"),
                tooltip: __("Reset to default values"),
                glyph: NOC.glyph.undo,
                handler: 'onResetRecord'
            },
            {
                itemId: "deleteBtn",
                text: __("Delete"),
                tooltip: __("Delete object"),
                glyph: NOC.glyph.times,
                handler: 'onDeleteRecord'
            },
            "-",
            {
                itemId: "createBtn",
                text: __("Add"),
                glyph: NOC.glyph.plus,
                tooltip: __("Add new record"),
                handler: "onNewRecord"
            },
            {
                itemId: "cloneBtn",
                text: __("Clone"),
                tooltip: __("Copy existing values to a new object"),
                glyph: NOC.glyph.copy,
                handler: "onCloneRecord"
            },
            "-",
            {
                itemId: "showMapBtn",
                xtype: "splitbutton",
                text: __("Show Map"),
                glyph: NOC.glyph.globe,
                menu: [ // Dynamically add items, in showMapHandler from Controller
                ],
            },
            {
                itemId: "configBtn",
                text: __("Config"),
                glyph: NOC.glyph.file,
                handler: "onConfig"
            },
            {
                itemId: "confDBBtn",
                text: __("ConfDB"),
                glyph: NOC.glyph.file_code_o,
                handler: "onConfDB"
            },
            {
                itemId: "cardBtn",
                text: __("Card"),
                glyph: NOC.glyph.eye,
                handler: "onCard"
            },
            {
                itemId: "dashboardBtn",
                text: __("Dashboard"),
                glyph: NOC.glyph.line_chart,
                tooltip: __("Show dashboard"),
                handler: "onDashboard"
            },
            {
                itemId: "consoleBtn",
                text: __("Console"),
                glyph: NOC.glyph.terminal,
                handler: "onConsole"
            },
            {
                itemId: "scriptsBtn",
                text: __("Scripts"),
                glyph: NOC.glyph.play,
                handler: "onScripts"
            },
            {
                itemId: "interfacesBtn",
                text: __("Interfaces"),
                glyph: NOC.glyph.reorder,
                handler: "onInterfaces"
            },
            {
                itemId: "sensorsBtn",
                text: __("Sensors"),
                glyph: NOC.glyph.thermometer_full,
                handler: "onSensors"
            },
            // {
            //     text: __("CPE"),
            //     glyph: NOC.glyph.share_alt,
            //     handler: "onCPE"
            // },
            {
                itemId: "linksBtn",
                text: __("Links"),
                glyph: NOC.glyph.link,
                handler: "onLinks"
            },
            {
                itemId: "discoverBtn",
                text: __("Discovery"),
                glyph: NOC.glyph.search,
                handler: "onDiscovery"
            },
            {
                itemId: "alarmsBtn",
                text: __("Alarms"),
                glyph: NOC.glyph.exclamation_triangle,
                handler: "onAlarm"
            },
            // {
            //     text: __("New Maintaince"),
            //     glyph: NOC.glyph.wrench,
            //     handler: "onMaintenance"
            // },
            {
                itemId: "inventoryBtn",
                text: __("Inventory"),
                glyph: NOC.glyph.list,
                handler: "onInventory"
            },
            {
                itemId: "cmdBtn",
                text: __("Command Log"),
                glyph: NOC.glyph.film,
                handler: "onInteractions"
            },
            // {
            //     text: __("Validation"),
            //     glyph: NOC.glyph.file,
            //     handler: "onValidationSettings"
            // },
            // {
            //     text: __("Capabilities"),
            //     glyph: NOC.glyph.file,
            //     handler: "onCaps"
            // },
            "->",
            {
                itemId: "helpBtn",
                glyph: NOC.glyph.question_circle,
                tooltip: __("Form Help"),
                handler: "onHelpOpener"

            }
        ]
    }],
});