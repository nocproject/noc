//---------------------------------------------------------------------
// vc.vctype application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vctype.Application");

Ext.define("NOC.vc.vctype.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.vc.vctype.Model"],
    model: "NOC.vc.vctype.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 200
        },

        {
            text: "Min. Labels",
            dataIndex: "min_labels",
            width: 70
        },

        {
            text: "L1",
            dataIndex: "l1"
        },

        {
            text: "L2",
            dataIndex: "l2"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "Name",
            allowBlank: false
        },
        {
            name: "min_labels",
            xtype: "numberfield",
            fieldLabel: "Min. Labels",
            allowBlank: false,
            minValue: 1,
            maxValue: 2,
            value: 1
        },
        {
            name: "label1_min",
            xtype: "numberfield",
            fieldLabel: "L1 (min)",
            allowBlank: false
        },
        {
            name: "label1_max",
            xtype: "numberfield",
            fieldLabel: "L1 (max)",
            allowBlank: false
        },
        {
            name: "label2_min",
            xtype: "numberfield",
            fieldLabel: "L2 (min)",
            allowBlank: true
        },
        {
            name: "label2_max",
            xtype: "numberfield",
            fieldLabel: "L2 (max)",
            allowBlank: true
        }
    ]
});
