//---------------------------------------------------------------------
// peer.asprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.asprofile.Application");

Ext.define("NOC.peer.asprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.peer.asprofile.Model",
        "NOC.ip.prefixprofile.LookupField",
        "NOC.core.ListFormField",
        "NOC.core.label.LabelField",
        "NOC.main.style.LookupField"
    ],
    model: "NOC.peer.asprofile.Model",
    search: true,
    viewModel: {
        data: {
            enableDiscoveryPrefixWhoisRoute: false
        }
    },
    rowClassField: "row_class",

    initComponent: function () {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    dataIndex: "name",
                    text: __("Name"),
                    width: 100
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
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
                    name: "validation_policy",
                    xtype: "combobox",
                    fieldLabel: __("Validation AS Field"),
                    labelWidth: 200,
                    allowBlank: false,
                    queryMode: "local",
                    displayField: "label",
                    valueField: "id",
                    store: {
                        fields: ["id", "label"],
                        data: [
                            {id: "S", label: "Strict (Required RIR)"},
                            {id: "O", label: "Optional (RIR & Org optional)"},
                        ]
                    },
                    defaultValue: "O",
                    uiStyle: "medium"
                },
                {
                    name: "gen_rpsl",
                    xtype: "checkbox",
                    boxLabel: __("Generate RPSL"),
                    allowBlank: true
                },
                {
                    name: "enable_discovery_peer",
                    xtype: "checkbox",
                    boxLabel: __("Peer Discovery"),
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    title: __("Discovery (Prefix)"),
                    layout: {
                        type: "table",
                        columns: 3
                    },
                    defaults: {
                        padding: "2px 4px 2px 4px"
                    },
                    items: [
                        {
                            xtype: "label",
                            text: __("Whois")
                        },
                        {
                            name: "enable_discovery_prefix_whois_route",
                            xtype: "checkbox",
                            reference: "enableDiscoveryPrefixWhoisRoute"
                        },
                        {
                            name: "prefix_profile_whois_route",
                            xtype: "ip.prefixprofile.LookupField",
                            allowBlank: true,
                            bind: {
                                disabled: "{!enableDiscoveryPrefixWhoisRoute.checked}"
                            }
                        }
                    ]
                },
                {
                    name: "match_rules",
                    xtype: "listform",
                    fieldLabel: __("Match Rules"),
                    rows: 5,
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
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
                            name: "include_expression",
                            xtype: "textfield",
                            fieldLabel: __("Include ASN Expression"),
                            allowBlank: true,
                            regex: /^\s*\d+\s*(-\d+\s*)?(,\s*\d+\s*(-\d+)?)*$/
                        },
                        {
                            name: "labels",
                            xtype: "labelfield",
                            fieldLabel: __("Match Labels"),
                            allowBlank: true,
                            isTree: true,
                            filterProtected: false,
                            pickerPosition: "down",
                            uiStyle: "extra",
                            query: {
                                "allow_matched": true,
                                "allow_models": ["peer.AS"],
                            }
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
