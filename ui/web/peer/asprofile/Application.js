//---------------------------------------------------------------------
// peer.asprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.asprofile.Application");

Ext.define("NOC.peer.asprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.peer.asprofile.Model",
        "NOC.ip.prefixprofile.LookupField",
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
                }
            ]
        });
        me.callParent();
    }
});
