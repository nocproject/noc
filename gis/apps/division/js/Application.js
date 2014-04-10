//---------------------------------------------------------------------
// gis.division application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.division.Application");

Ext.define("NOC.gis.division.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.gis.division.Model",
        "NOC.gis.division.LookupField",
        "Ext.ux.form.DictField"
    ],
    model: "NOC.gis.division.Model",
    search: true,
    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            columns: [
                {
                    text: "Type",
                    dataIndex: "type",
                    width: 100,
                    renderer: NOC.render.Choices({
                        A: "Administrative"
                    })
                },
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
                    name: "type",
                    xtype: "combobox",
                    fieldLabel: "Type",
                    allowBlank: false,
                    store: [
                        ["A", "Administrative"]
                    ],
                    defaultValue: "A"
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
