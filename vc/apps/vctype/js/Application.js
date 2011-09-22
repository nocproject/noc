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
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },

        {
            text: "Min. Labels",
            dataIndex: "min_labels"
        },

        {
            text: "L1 (min)",
            dataIndex: "label1_min"
        },

        {
            text: "L1 (max)",
            dataIndex: "label1_max"
        },

        {
            text: "L2 (min)",
            dataIndex: "label2_min"
        },

        {
            text: "L2 (max)",
            dataIndex: "label2_max"
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
