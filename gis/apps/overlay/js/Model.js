//---------------------------------------------------------------------
// gis.overlay Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.overlay.Model");

Ext.define("NOC.gis.overlay.Model", {
    extend: "Ext.data.Model",
    rest_url: "/gis/overlay/",

    fields: [
        {
            name: "id",
            type: "string"
        },

        {
            name: "name",
            type: "string"
        },
        {
            name: "plugin",
            type: "string"
        },
        {
            name: "gate_id",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "permission_name",
            type: "string"
        }
    ]
});
