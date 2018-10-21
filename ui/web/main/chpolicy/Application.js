//---------------------------------------------------------------------
// main.chpolicy application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.chpolicy.Application");

Ext.define("NOC.main.chpolicy.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.chpolicy.Model"
    ],
    model: "NOC.main.chpolicy.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Table"),
                    dataIndex: "table",
                    width: 200
                },
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    width: 25,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Dry Run"),
                    dataIndex: "dry_run",
                    width: 25,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("TTL"),
                    dataIndex: "ttl",
                    width: 100,
                    renderer: function(v) {
                        if(v && v > 0) {
                            return v
                        }
                        return __("Disabled")
                    }
                }
            ],

            fields: [
                {
                    name: "table",
                    xtype: "textfield",
                    fieldLabel: __("Table"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },
                {
                    name: "dry_run",
                    xtype: "checkbox",
                    boxLabel: __("Dry Run")
                },
                {
                    name: "ttl",
                    xtype: "numberfield",
                    fieldLabel: __("TTL (days)"),
                    allowBlank: false,
                    minValue: 0,
                    uiStyle: "small"
                }
            ]
        });
        me.callParent();
    },
    filters: [
        {
            title: __("By Active"),
            name: "is_active",
            ftype: "boolean"
        },
        {
            title: __("By Dry Run"),
            name: "dry_run",
            ftype: "boolean"
        }
    ]
});
