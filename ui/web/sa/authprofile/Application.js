//---------------------------------------------------------------------
// sa.authprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.authprofile.Application");

Ext.define("NOC.sa.authprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.PasswordField",
        "NOC.core.label.LabelField",
        "NOC.sa.authprofile.Model",
        "NOC.main.handler.LookupField",
        "NOC.core.ListFormField",
        "NOC.main.remotesystem.LookupField"
    ],
    model: "NOC.sa.authprofile.Model",
    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Type"),
                    dataIndex: "type",
                    width: 100,
                    renderer: NOC.render.Choices({
                        G: "Local Group",
                        R: "RADIUS",
                        T: "TACACS+",
                        L: "LDAP",
                        S: "Suggest"
                    })
                },
                {
                    text: __("User"),
                    dataIndex: "user",
                    width: 100
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
                    name: "type",
                    xtype: "combobox",
                    fieldLabel: __("Type"),
                    allowBlank: false,
                    store: [
                        ["G", "Local Group"],
                        ["R", "RADIUS"],
                        ["T", "TACACS+"],
                        ["L", "LDAP"]
                    ]
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    uiStyle: "extra",
                    query: {
                        "enable_authprofile": true
                    }
                },
                {
                    name: "user",
                    xtype: "textfield",
                    fieldLabel: __("User"),
                    allowBlank: true
                },
                {
                    name: "password",
                    xtype: "password",
                    fieldLabel: __("Password"),
                    uiStyle: "large",
                    allowBlank: true
                },
                {
                    name: "super_password",
                    xtype: "password",
                    fieldLabel: __("Super Password"),
                    uiStyle: "large",
                    allowBlank: true
                },
                {
                    name: "snmp_security_level",
                    xtype: "combobox",
                    fieldLabel: __("SNMP Security Level"),
                    uiStyle: "large",
                    store: [
                        ["Community", "Community"],
                        ["noAuthNoPriv", "No Auth No Priv"],
                        ["authNoPriv", "Auth No Priv"],
                        ["authPriv", "Auth Priv"]
                    ],
                    queryMode: "local",
                    listeners: {
                        change: me.onChangeSNMP_SecurityLevel
                    }
                },
                {
                    name: "snmp_ro",
                    xtype: "password",
                    fieldLabel: __("SNMP RO Community"),
                    uiStyle: "large",
                    readOnlyCls: 'x-item-disabled',
                    allowBlank: true
                },
                {
                    name: "snmp_rw",
                    xtype: "password",
                    fieldLabel: __("SNMP RW Community"),
                    uiStyle: "large",
                    readOnlyCls: 'x-item-disabled',
                    allowBlank: true
                },
                {
                    name: "snmp_username",
                    xtype: "textfield",
                    fieldLabel: __("SNMP Username"),
                    uiStyle: "large",
                    readOnlyCls: 'x-item-disabled',
                    allowBlank: true,
                    groupEdit: true
                },
                {
                    name: "snmp_ctx_name",
                    xtype: "textfield",
                    fieldLabel: __("SNMP Context Name"),
                    allowBlank: true,
                    uiStyle: "large",
                    readOnlyCls: 'x-item-disabled',
                    groupEdit: true
                },
                {
                    xtype: "fieldcontainer",
                    itemId: "snmp_auth_proto",
                    fieldLabel: __("SNMP Auth Proto"),
                    visible: false,
                    maxWidth: 200,
                    defaultType: "radiofield",
                    defaults: {
                        flex: 1
                    },
                    layout: "hbox",
                    items: [
                        {
                            boxLabel: 'MD5',
                            name: 'snmp_auth_proto',
                            padding: "0 5",
                            inputValue: "MD5",
                        },
                        {
                            boxLabel: "SHA",
                            name: 'snmp_auth_proto',
                            inputValue: "SHA",
                        }
                    ]
                },
                {
                    xtype: "password",
                    fieldLabel: __("SNMP Auth Key"),
                    visible: false,
                    uiStyle: "large",
                    name: "snmp_auth_key",
                    allowBlank: true,
                    groupEdit: true
                },
                {
                    xtype: "fieldcontainer",
                    itemId: "snmp_priv_proto",
                    fieldLabel: __("SNMP Priv Proto"),
                    visible: false,
                    maxWidth: 200,
                    defaultType: "radiofield",
                    defaults: {
                        flex: 1
                    },
                    layout: "hbox",
                    items: [
                        {
                            boxLabel: "DES",
                            name: 'snmp_priv_proto',
                            padding: "0 5",
                            inputValue: "DES",
                        },
                        {
                            boxLabel: "AES",
                            name: 'snmp_priv_proto',
                            inputValue: "AES",
                        }
                    ]
                },
                {
                    xtype: "password",
                    fieldLabel: __("SNMP Priv Key"),
                    visible: false,
                    uiStyle: "large",
                    name: "snmp_priv_key",
                    allowBlank: true,
                    groupEdit: true
                },
                {
                    name: "enable_suggest_by_rule",
                    xtype: "checkboxfield",
                    boxLabel: __("Enable Suggets By Rule"),
                    tooltip: __("If check - use Credential Check Rules (Service Activation -> Setup -> Credential Check Rules)<br/>" +
                        " for suggest credential"),
                    allowBlank: true,
                    listeners: {
                        render: me.addTooltip
                    }
                },
                {
                    name: "preferred_profile_credential",
                    xtype: "checkboxfield",
                    boxLabel: __("Preferred Profile Credential"),
                    tooltip: __("If set - Credential on Profile will replace credential on Device"),
                    allowBlank: true,
                    listeners: {
                        render: me.addTooltip
                    }
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
                    name: "dynamic_classification_policy",
                    xtype: "combobox",
                    fieldLabel: __("Dynamic Classification Policy"),
                    store: [
                        ["D", __("Disabled")],
                        ["R", __("By Rule")],
                        ["U", __("By Username/SNMP RO")],
                    ],
                    allowBlank: false,
                    labelWidth: 200,
                    value: "R",
                    uiStyle: "medium"
                },
                {
                    name: "match_rules",
                    xtype: "listform",
                    rows: 5,
                    labelAlign: "top",
                    uiStyle: "large",
                    fieldLabel: __("Match Rules"),
                    items: [
                        {
                            name: "dynamic_order",
                            xtype: "numberfield",
                            fieldLabel: __("Dynamic Order"),
                            allowBlank: true,
                            defaultValue: 0,
                            uiStyle: "small"
                        },
                        {
                            name: "labels",
                            xtype: "labelfield",
                            fieldLabel: __("Match Labels"),
                            allowBlank: false,
                            isTree: true,
                            filterProtected: false,
                            pickerPosition: "down",
                            uiStyle: "extra",
                            query: {
                                "allow_matched": true
                            }
                        },
                        {
                            name: "handler",
                            xtype: "main.handler.LookupField",
                            fieldLabel: __("Match Handler"),
                            allowBlank: true,
                            uiStyle: "medium",
                            query: {
                                "allow_match_rule": true
                            }
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    onChangeSNMP_SecurityLevel: function(field, value) {
        var form = this.up();
        form.down('[name=snmp_ro]').setReadOnly(!["Community"].includes(value));
        form.down('[name=snmp_rw]').setReadOnly(!["Community"].includes(value));
        form.down('[name=snmp_username]').setReadOnly(!["noAuthNoPriv", "authNoPriv", "authPriv"].includes(value));
        form.down('[name=snmp_ctx_name]').setReadOnly(!["noAuthNoPriv", "authNoPriv", "authPriv"].includes(value));
        form.down('[itemId=snmp_auth_proto]').setHidden(["Community", "noAuthNoPriv"].includes(value));
        form.down('[name=snmp_auth_key]').setHidden(["Community", "noAuthNoPriv"].includes(value));
        form.down('[itemId=snmp_priv_proto]').setHidden(["Community", "noAuthNoPriv", "authNoPriv"].includes(value));
        form.down('[name=snmp_priv_key]').setHidden(["Community", "noAuthNoPriv", "authNoPriv"].includes(value));
    },
});
