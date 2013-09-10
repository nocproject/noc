//---------------------------------------------------------------------
// sa.managedobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.Application");

Ext.define("NOC.sa.managedobject.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.core.TagsField",
        "NOC.sa.managedobject.Model",
        "NOC.sa.managedobject.AttributesModel",
        "NOC.sa.managedobject.SchemeLookupField",
        "NOC.sa.administrativedomain.LookupField",
        "NOC.sa.activator.LookupField",
        "NOC.sa.managedobjectprofile.LookupField",
        "NOC.vc.vcdomain.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.main.pyrule.LookupField",
        "NOC.main.ref.profile.LookupField",
        "NOC.main.ref.stencil.LookupField"
    ],
    model: "NOC.sa.managedobject.Model",
    search: true,
    rowClassField: "row_class",

    //
    initComponent: function() {
        var me = this;

        me.configPreviewButton = Ext.create("Ext.button.Button", {
            text: "Config",
            glyph: NOC.glyph.file,
            scope: me,
            handler: me.onConfig
        });

        me.consoleButton = Ext.create("Ext.button.Button", {
            text: "Console",
            glyph: NOC.glyph.terminal,
            scope: me,
            handler: me.onConsole
        });

        me.scriptsButton = Ext.create("Ext.button.Button", {
            text: "Scripts",
            glyph: NOC.glyph.play,
            disabled: true,
            scope: me,
            handler: me.onInterfaces
        });

        me.interfacesButton = Ext.create("Ext.button.Button", {
            text: "Interfaces",
            glyph: NOC.glyph.reorder,
            scope: me,
            handler: me.onInterfaces
        });

        me.linksButton = Ext.create("Ext.button.Button", {
            text: "Links",
            glyph: NOC.glyph.link,
            scope: me,
            handler: me.onLinks
        });

        me.discoveryButton = Ext.create("Ext.button.Button", {
            text: "Discovery",
            glyph: NOC.glyph.search,
            scope: me,
            handler: me.onDiscovery
        });

        me.alarmsButton = Ext.create("Ext.button.Button", {
            text: "Alarms",
            glyph: NOC.glyph.warning_sign,
            disabled: true,
            scope: me,
            handler: me.onInterfaces
        });

        me.ITEM_CONFIG = me.registerItem(
            Ext.create("NOC.core.RepoPreview", {
                app: me,
                previewName: "{{name}} config",
                restUrl: "/sa/managedobject/{{id}}/repo/cfg/"
            })
        );

        me.ITEM_CONSOLE = me.registerItem(
            Ext.create("NOC.sa.managedobject.ConsolePanel", {app: me})
        );

        me.ITEM_INTERFACE = me.registerItem(
            Ext.create("NOC.sa.managedobject.InterfacePanel", {app: me})
        );

        me.ITEM_LINKS = me.registerItem(
            Ext.create("NOC.sa.managedobject.LinksPanel", {app: me})
        );

        me.ITEM_DISCOVERY = me.registerItem(
            Ext.create("NOC.sa.managedobject.DiscoveryPanel", {app: me})
        );

        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name"
                },
                {
                    text: "Managed",
                    dataIndex: "is_managed",
                    width: 30,
                    renderer: NOC.render.Bool
                },
                {
                    text: "Platform",
                    dataIndex: "platform",
                    width: 150
                },
                {
                    text: "SA Profile",
                    dataIndex: "profile_name"
                },
                {
                    text: "Obj. Profile",
                    dataIndex: "object_profile",
                    renderer: NOC.render.Lookup("object_profile")
                },
                {
                    text: "Adm. Domain",
                    dataIndex: "administrative_domain",
                    renderer: NOC.render.Lookup("administrative_domain"),
                    width: 120
                },
                {
                    text: "VRF",
                    dataIndex: "vrf",
                    renderer: NOC.render.Lookup("vrf")
                },
                {
                    text: "Address",
                    dataIndex: "address"
                },
                {
                    text: "Activator",
                    dataIndex: "activator",
                    renderer: NOC.render.Lookup("activator")
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1
                },
                {
                    text: "Interfaces",
                    dataIndex: "interface_count",
                    width: 50,
                    align: "right",
                    renderer: NOC.render.Clickable,
                    onClick: me.onInterfaceClick
                },
                {
                    text: "Links",
                    dataIndex: "link_count",
                    width: 50,
                    align: "right",
                    renderer: NOC.render.Clickable,
                    onClick: me.onLinkClick
                },
                {
                    text: "Tags",
                    dataIndex: "tags",
                    renderer: NOC.render.Tags,
                    width: 100
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
                    name: "is_managed",
                    xtype: "checkboxfield",
                    boxLabel: "Is Managed?",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textfield",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    name: "object_profile",
                    xtype: "sa.managedobjectprofile.LookupField",
                    fieldLabel: "Object Profile",
                    allowBlank: false
                },
                {
                    name: "shape",
                    xtype: "main.ref.stencil.LookupField",
                    fieldLabel: "Shape",
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    title: "Location",
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "administrative_domain",
                            xtype: "sa.administrativedomain.LookupField",
                            fieldLabel: "Administrative Domain",
                            width: 200,
                            allowBlank: false
                        },
                        {
                            name: "activator",
                            xtype: "sa.activator.LookupField",
                            fieldLabel: "Activator",
                            width: 100,
                            allowBlank: false
                        },
                        {
                            name: "vrf",
                            xtype: "ip.vrf.LookupField",
                            fieldLabel: "VRF",
                            allowBlank: true
                        },
                        {
                            name: "vc_domain",
                            xtype: "vc.vcdomain.LookupField",
                            fieldLabel: "VC Domain",
                            allowBlank: true
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: "Access",
                    items: [
                        {
                            name: "profile_name",
                            xtype: "main.ref.profile.LookupField",
                            fieldLabel: "SA Profile",
                            allowBlank: false
                        },
                        {
                            name: "scheme",
                            xtype: "sa.managedobject.SchemeLookupField",
                            fieldLabel: "Scheme",
                            allowBlank: false
                        },
                        {
                            name: "address",
                            xtype: "textfield",
                            fieldLabel: "Address",
                            allowBlank: false
                        },
                        {
                            name: "port",
                            xtype: "numberfield",
                            fieldLabel: "Port",
                            allowBlank: true
                        },
                        {
                            name: "user",
                            xtype: "textfield",
                            fieldLabel: "User",
                            allowBlank: true
                        },
                        {
                            name: "password",
                            xtype: "textfield",
                            fieldLabel: "Password",
                            allowBlank: true,
                            inputType: "password"
                        },
                        {
                            name: "super_password",
                            xtype: "textfield",
                            fieldLabel: "Super Password",
                            allowBlank: true,
                            inputType: "password"
                        },
                        {
                            name: "remote_path",
                            xtype: "textfield",
                            fieldLabel: "Path",
                            allowBlank: true
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
                            name: "trap_source_ip",
                            xtype: "textfield",
                            fieldLabel: "Trap Source IP",
                            allowBlank: true
                        },
                        {
                            name: "trap_community",
                            xtype: "textfield",
                            fieldLabel: "Trap Community",
                            allowBlank: true
                        },
                        {
                            name: "snmp_ro",
                            xtype: "textfield",
                            fieldLabel: "RO Community",
                            allowBlank: true
                        },
                        {
                            name: "snmp_rw",
                            xtype: "textfield",
                            fieldLabel: "RW Community",
                            allowBlank: true
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: "Rules",
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "config_filter_rule",
                            xtype: "main.pyrule.LookupField",
                            fieldLabel: "Config Filter pyRule",
                            allowBlank: true
                        },
                        {
                            name: "config_diff_filter_rule",
                            xtype: "main.pyrule.LookupField",
                            fieldLabel: "Config Diff Filter Rule",
                            allowBlank: true
                        },
                        {
                            name: "config_validation_rule",
                            xtype: "main.pyrule.LookupField",
                            fieldLabel: "Config Validation pyRule",
                            allowBlank: true
                        }
                    ]
                },
                {
                    name: "max_scripts",
                    xtype: "numberfield",
                    fieldLabel: "Max. Scripts",
                    allowBlank: true
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: "Tags",
                    allowBlank: true
                }
            ],
            formToolbar: [
                me.consoleButton,
                me.scriptsButton,
                me.configPreviewButton,
                me.interfacesButton,
                me.linksButton,
                me.discoveryButton,
                me.alarmsButton
            ]
        });
        me.callParent();
    },
    filters: [
        // @todo: By SA Profile
        {
            title: "By Managed",
            name: "is_managed",
            ftype: "boolean"
        },
        {
            title: "By Obj. Profile",
            name: "object_profile",
            ftype: "lookup",
            lookup: "sa.managedobjectprofile"
        },
        {
            title: "By Adm. Domain",
            name: "administrative_domain",
            ftype: "lookup",
            lookup: "sa.administrativedomain"
        },
        {
            title: "By Activator",
            name: "activator",
            ftype: "lookup",
            lookup: "sa.activator"
        },
        {
            title: "By Tags",
            name: "tags",
            ftype: "tag"
        }
    ],
    inlines: [
        {
            title: "Attributes",
            model: "NOC.sa.managedobject.AttributesModel",
            columns: [
                {
                    text: "Key",
                    dataIndex: "key",
                    width: 100,
                    editor: "textfield"
                },
                {
                    text: "Value",
                    dataIndex: "value",
                    editor: "textfield",
                    flex: 1
                }
            ]
        }
    ],
    //
    onConsole: function() {
        var me = this;
        me.showItem(me.ITEM_CONSOLE).preview(me.currentRecord);
    },
    //
    onConfig: function() {
        var me = this;
        me.showItem(me.ITEM_CONFIG).preview(me.currentRecord);
    },
    //
    onInterfaces: function() {
        var me = this;
        me.showItem(me.ITEM_INTERFACE).preview(me.currentRecord);
    },
    //
    onLinks: function() {
        var me = this;
        me.showItem(me.ITEM_LINKS).preview(me.currentRecord);
    },
    //
    onDiscovery: function() {
        var me = this;
        me.showItem(me.ITEM_DISCOVERY).preview(me.currentRecord);
    },
    //
    onInterfaceClick: function(record) {
        var me = this;
        me.onEditRecord(record);
        me.onInterfaces();
    },
    //
    onLinkClick: function(record) {
        var me = this;
        me.onEditRecord(record);
        me.onLinks();
    }
});
