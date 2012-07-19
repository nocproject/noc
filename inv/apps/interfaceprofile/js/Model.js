//---------------------------------------------------------------------
// inv.interfaceprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interfaceprofile.Model");

Ext.define("NOC.inv.interfaceprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/interfaceprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "link_events",
            type: "string",
            defaultValue: "A"
        }
    ]
});
