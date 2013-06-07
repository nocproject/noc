//---------------------------------------------------------------------
// pm.check application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.check.Application");

Ext.define("NOC.pm.check.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.pm.pmcheck.Model",
        "NOC.pm.storage.LookupField",
        "NOC.pm.probe.LookupField"
    ],
    model: "NOC.pm.check.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 200
        },
        {
            text: "Active",
            dataIndex: "is_active",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Storage",
            dataIndex: "storage",
            renderer: NOC.render.Lookup("storage"),
            width: 150
        },
        {
            text: "Probe",
            dataIndex: "probe",
            renderer: NOC.render.Lookup("probe"),
            width: 150
        },
        {
            text: "Interval",
            dataIndex: "interval",
            width: 75
        }
    ],

    filters: [
        {
            title: "Is Active",
            name: "is_active",
            ftype: "boolean"
        }
    ],

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            fields: [
                {
                    name: "name",
                    fieldLabel: "Name",
                    xtype: "textfield",
                    allowBlank: false
                },
                {
                    name: "is_active",
                    xtype: "checkboxfield",
                    boxLabel: "Active"
                },
                {
                    name: "probe",
                    fieldLabel: "Probe",
                    xtype: "pm.probe.LookupField",
                    allowBlank: false
                },
                {
                    name: "storage",
                    fieldLabel: "Storage",
                    xtype: "pm.storage.LookupField",
                    allowBlank: false
                },
                {
                    name: "interval",
                    fieldLabel: "Interval",
                    xtype: "numberfield",
                    allowBlank: false,
                    defaultValue: 60
                }
            ]
        });
        me.callParent();
    }
});
