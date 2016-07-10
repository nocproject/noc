//---------------------------------------------------------------------
// fm.mib Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.mib.Model");

Ext.define("NOC.fm.mib.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/mib/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "last_updated",
            type: "auto"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "depends_on",
            type: "auto"
        },
        {
            name: "version",
            type: "int"
        },
        {
            name: "typedefs",
            type: "auto"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
