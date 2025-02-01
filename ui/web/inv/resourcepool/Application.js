//---------------------------------------------------------------------
// inv.resourcepool application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.resourcepool.Application");

Ext.define("NOC.inv.resourcepool.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.resourcepool.Model"
    ],
    model: "NOC.inv.resourcepool.Model",
    search: true,
    helpId: "reference-allocation-group",

    initComponent: function() {
        var me = this;

        me.cardButton = Ext.create("Ext.button.Button", {
            text: __("Card"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onCard
        });

        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    flex: 150
                },
                {
                    text: "Type",
                    dataIndex: "type",
                    flex: 100
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true,
                    uiStyle: "large"
                },
                {
                    name: "type",
                    xtype: "combobox",
                    fieldLabel: __("Type"),
                    allowBlank: false,
                    uiStyle: "medium",
                    store: [
                        ["ip", "IP"],
                        ["vlan", "VLAN"]
                    ]
                },
                {
                    name: "is_unique",
                    xtype: "checkbox",
                    boxLabel: __("Unique Resource")
                },
                {
                    name: "strategy",
                    xtype: "combobox",
                    fieldLabel: __("Allocate Strategy"),
                    value: "F",
                    uiStyle: "medium",
                    store: [
                        ["F", "First"],
                        ["L", "Last"],
                        ["R", "Random"]
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("API"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "api_code",
                            xtype: "textfield",
                            fieldLabel: __("API Code"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "api_role",
                            xtype: "textfield",
                            fieldLabel: __("API Role"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                    ]
                }
            ],
            formToolbar: [
                me.cardButton
            ]
        });
        me.callParent();
    },

    onCard: function() {
        var me = this;
        if(me.currentRecord) {
            window.open(
                "/api/card/view/resourcepool/" + me.currentRecord.get("id") + "/"
            );
        }
    }
});