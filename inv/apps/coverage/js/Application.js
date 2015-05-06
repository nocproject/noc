//---------------------------------------------------------------------
// inv.coverage application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.coverage.Application");

Ext.define("NOC.inv.coverage.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.coverage.Model",
        "NOC.inv.coverage.BuildingModel",
        "NOC.inv.coverage.ObjectModel"
    ],
    model: "NOC.inv.coverage.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name"
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
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description"
        }
    ],
    inlines: [
        {
            title: "Covered Buildings",
            model: "NOC.inv.coverage.BuildingModel",
            columns: [
                {
                    text: "Pref.",
                    tooltip: "Preference",
                    dataIndex: "preference",
                    width: 50,
                    textAlign: "right"
                },
                {
                    text: "Building",
                    dataIndex: "building",
                    renderer: NOC.render.Lookup("building"),
                    flex: 1
                },
                {
                    text: "Entrance",
                    dataIndex: "entrance",
                    width: 100
                }
            ]
        },
        {
            title: "Covered Objects",
            model: "NOC.inv.coverage.ObjectModel",
            columns: [
                {
                    text: "Pref.",
                    tooltip: "Preference",
                    dataIndex: "preference",
                    width: 50,
                    textAlign: "right"
                },
                {
                    text: "Object",
                    dataIndex: "object",
                    renderer: NOC.render.Lookup("object"),
                    flex: 1
                }
            ]
        }
    ]
});
