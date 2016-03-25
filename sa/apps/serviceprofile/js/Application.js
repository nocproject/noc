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
        "NOC.main.ref.glyph.LookupField"
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
                        return "<i class='" + v + "></i>";
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
                    name: "label_template",
                    xtype: "textfield",
                    fieldLabel: "Label Template",
                    uiStyle: "extra",
                    allowBlank: true
                },
                {
                    name: "glyph",
                    xtype: "main.ref.glyph.LookupField",
                    fieldLabel: "Handler",
                    allowBlank: true,
                    uiStyle: "large"
                }
            ]
        });
        me.callParent();
    }
});
