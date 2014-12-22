//---------------------------------------------------------------------
// gis.srs Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.srs.Model");

Ext.define("NOC.gis.srs.Model", {
    extend: "Ext.data.Model",
    rest_url: "/gis/srs/",
    idProperty: "srid",

    fields: [
        {
            name: "srid",
            type: "int"
        },
        {
            name: "auth_name",
            type: "string"
        },
        {
            name: "auth_srid",
            type: "int"
        },
        {
            name: "proj4text",
            type: "string"
        }
    ]
});
