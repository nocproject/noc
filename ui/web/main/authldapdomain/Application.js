//---------------------------------------------------------------------
// main.authldapdomain application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.authldapdomain.Application");

Ext.define("NOC.main.authldapdomain.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.authldapdomain.Model",
        "NOC.main.group.LookupField"
    ],
    model: "NOC.main.authldapdomain.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 100
                },
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    width: 50,
                    renderer: NOC.render.Bool
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    uiStyle: "medium",
                    allowBlank: false
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "type",
                    xtype: "combobox",
                    fieldLabel: __("Type"),
                    store: [
                        ["ldap", "LDAP"],
                        ["ad", "Active Directory"]
                    ],
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "root",
                    xtype: "textfield",
                    fieldLabel: __("Root"),
                    allowBlank: false
                },
                {
                    name: "user_search_filter",
                    xtype: "textfield",
                    fieldLabel: __("User Search Filter"),
                    allowBlank: true
                },
                {
                    name: "group_search_filter",
                    xtype: "textfield",
                    fieldLabel: __("Group Search Filter"),
                    allowBlank: true
                },
                {
                    name: "bind_user",
                    xtype: "textfield",
                    fieldLabel: __("Bind User"),
                    allowBlank: true
                },
                {
                    name: "bind_password",
                    xtype: "textfield",
                    fieldLabel: __("Bind Password"),
                    allowBlank: true
                },
                {
                    name: "require_group",
                    xtype: "textfield",
                    fieldLabel: __("Require Group"),
                    allowBlank: true
                },
                {
                    name: "deny_group",
                    xtype: "textfield",
                    fieldLabel: __("Deny Group"),
                    allowBlank: true
                },
                {
                    name: "servers",
                    xtype: "gridfield",
                    fieldLabel: __("Servers"),
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "name",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: __("Active"),
                            dataIndex: "is_active",
                            width: 50,
                            editor: "checkbox"
                        },
                        {
                            text: __("Address"),
                            dataIndex: "address",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: __("Port"),
                            dataIndex: "port",
                            width: 50,
                            editor: "numberfield"
                        },
                        {
                            text: __("Use TLS"),
                            dataIndex: "use_tls",
                            width: 50,
                            editor: "checkbox"
                        }
                    ]
                },
                {
                    name: "convert_username",
                    xtype: "combobox",
                    fieldLabel: __("Convert Username"),
                    store: [
                        ["0", __("Do not convert")],
                        ["l", __("Lowercase")],
                        ["u", __("Uppercase")]
                    ],
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "require_any_group",
                    xtype: "checkbox",
                    boxLabel: __("Require any group")
                },
                {
                    name: "groups",
                    xtype: "gridfield",
                    fieldLabel: __("Groups"),
                    columns: [
                        {
                            text: __("LDAP Group DN"),
                            dataIndex: "group_dn",
                            width: 200,
                            editor: "textfield"
                        },
                        {
                            text: __("Active"),
                            dataIndex: "is_active",
                            width: 50,
                            editor: "checkbox",
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Local Group"),
                            dataIndex: "group",
                            flex: 1,
                            editor: "main.group.LookupField",
                            renderer: NOC.render.Lookup("group")
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
