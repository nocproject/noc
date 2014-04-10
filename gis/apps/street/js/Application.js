//---------------------------------------------------------------------
// gis.street application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.street.Application");

Ext.define("NOC.gis.street.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.gis.street.Model",
        "NOC.gis.division.LookupField",
        "Ext.ux.form.DictField"
    ],
    model: "NOC.gis.street.Model",
    search: true,
    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            columns: [
                {
                    text: "Short",
                    dataIndex: "short_name",
                    width: 50
                },
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 300
                },
                {
                    text: "Active",
                    dataIndex: "is_active",
                    renderer: NOC.render.Bool,
                    width: 25
                },
                {
                    text: "Parent",
                    dataIndex: "full_parent",
                    flex: 1,
                    sort: false
                }
            ],
            fields: [
                {
                    name: "full_path",
                    xtype: "displayfield",
                    fieldLabel: "Full Path"
                },
                {
                    name: "parent",
                    xtype: "gis.division.LookupField",
                    fieldLabel: "Parent"
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false
                },
                {
                    name: "short_name",
                    xtype: "textfield",
                    fieldLabel: "Short Name",
                    allowBlank: true
                },
                {
                    name: "is_active",
                    xtype: "checkboxfield",
                    boxLabel: "Active"
                },
                {
                    xtype: "dictfield",
                    name: "data",
                    fieldLabel: "Data",
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    },
    filters: [
        {
            title: "By Parent",
            name: "parent",
            ftype: "lookup",
            lookup: "gis.division"
        }
    ]
});
