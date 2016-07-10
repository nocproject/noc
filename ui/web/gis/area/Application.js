//---------------------------------------------------------------------
// gis.area application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.area.Application");

Ext.define("NOC.gis.area.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.gis.area.Model",
        "Ext.ux.form.GeoField"
    ],
    model: "NOC.gis.area.Model",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },

        {
            text: "Active",
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
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
            allowBlank: false
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Active"
        },
        {
            name: "SW",
            xtype: "geofield",
            fieldLabel: "SW",
            allowBlank: false
        },
        {
            name: "NE",
            xtype: "geofield",
            fieldLabel: "NE",
            allowBlank: false
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
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: "Description",
            allowBlank: true
        }
    ]
});
