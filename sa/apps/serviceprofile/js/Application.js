//---------------------------------------------------------------------
// sa.serviceprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.serviceprofile.Application");

Ext.define("NOC.sa.serviceprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.serviceprofile.Model",
        "NOC.main.ref.glyph.LookupField",
        "NOC.inv.interfaceprofile.LookupField"
    ],
    model: "NOC.sa.serviceprofile.Model",
    search: true,

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            columns: [
                {
                    text: "Glyph",
                    data_index: "glyph",
                    width: 25,
                    renderer: function(v) {
                        if(v !== undefined && v !== "")
                        {
                            return "<i class='" + v + "'></i>";
                        } else {
                            return "";
                        }
                    }
                },
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true,
                    uiStyle: "extra"
                },
                {
                    name: "card_title_template",
                    xtype: "textfield",
                    fieldLabel: "Title Template",
                    uiStyle: "extra",
                    allowBlank: true
                },
                {
                    name: "glyph",
                    xtype: "main.ref.glyph.LookupField",
                    fieldLabel: "Icon",
                    allowBlank: true,
                    uiStyle: "large"
                },
                {
                    name: "interface_profile",
                    xtype: "inv.interfaceprofile.LookupField",
                    fieldLabel: "Interface Profile",
                    allowBlank: true
                },
                {
                    name: "weight",
                    xtype: "numberfield",
                    fieldLabel: "Alarm weight",
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
