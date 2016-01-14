//---------------------------------------------------------------------
// crm.supplierprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.supplierprofile.Application");

Ext.define("NOC.crm.supplierprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.crm.supplierprofile.Model",
        "NOC.main.style.LookupField"
    ],
    model: "NOC.crm.supplierprofile.Model",
    search: true,
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    flex: 1
                },
                {
                    text: "Tags",
                    dataIndex: "tags",
                    width: 150,
                    render: NOC.render.Tags
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
                    uiStyle: "expand"
                },
                {
                    name: "style",
                    xtype: "main.style.LookupField",
                    fieldLabel: "Style",
                    allowBlank: true
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: "Tags",
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
