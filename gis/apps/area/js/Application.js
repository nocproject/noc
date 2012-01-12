//---------------------------------------------------------------------
// gis.area application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.area.Application");

Ext.define("NOC.gis.area.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.gis.area.Model"],
    model: "NOC.gis.area.Model",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },

        {
            text: "Active",
            dataIndex: "is_active"
        },

        {
            text: "SW",
            dataIndex: "SW"
        },

        {
            text: "NE",
            dataIndex: "NE"
        },

        {
            text: "Min. Zoom",
            dataIndex: "min_zoom"
        },

        {
            text: "Max. Zoom",
            dataIndex: "max_zoom"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "name",
            allowBlank: true
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "is_active"
        },
        {
            name: "SW",
            xtype: "textfield",
            fieldLabel: "SW",
            allowBlank: true
        },
        {
            name: "NE",
            xtype: "textfield",
            fieldLabel: "NE",
            allowBlank: true
        },
        {
            name: "min_zoom",
            xtype: "numberfield",
            fieldLabel: "Min. Zoom",
            allowBlank: false,
            defaultValue: 0,
            minValue: 0,
            maxValue: 18
        },
        {
            name: "max_zoom",
            xtype: "numberfield",
            fieldLabel: "Max. Zoom",
            allowBlank: false,
            defaultValue: 18,
            minValue: 0,
            maxValue: 18
        }
    ]
});
