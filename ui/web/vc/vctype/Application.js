//---------------------------------------------------------------------
// vc.vctype application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vctype.Application");

Ext.define("NOC.vc.vctype.Application", {
    extend: "NOC.core.ModelApplication",
    requires: ["NOC.vc.vctype.Model"],
    model: "NOC.vc.vctype.Model",
    search: true,
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 200
        },

        {
            text: __("Min. Labels"),
            dataIndex: "min_labels",
            width: 70
        },

        {
            text: __("L1"),
            dataIndex: "l1"
        },

        {
            text: __("L2"),
            dataIndex: "l2"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: __("Name"),
            allowBlank: false
        },
        {
            name: "min_labels",
            xtype: "numberfield",
            fieldLabel: __("Min. Labels"),
            allowBlank: false,
            minValue: 1,
            maxValue: 2,
            value: 1
        },
        {
            name: "label1_min",
            xtype: "numberfield",
            fieldLabel: __("L1 (min)"),
            allowBlank: false
        },
        {
            name: "label1_max",
            xtype: "numberfield",
            fieldLabel: __("L1 (max)"),
            allowBlank: false
        },
        {
            name: "label2_min",
            xtype: "numberfield",
            fieldLabel: __("L2 (min)"),
            allowBlank: true
        },
        {
            name: "label2_max",
            xtype: "numberfield",
            fieldLabel: __("L2 (max)"),
            allowBlank: true
        }
    ]
});
