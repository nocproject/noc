//---------------------------------------------------------------------
// inv.pendinglink Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.pendinglink.Model");

Ext.define("NOC.inv.pendinglink.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/pendinglink/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "local_object",
            type: "string"
        },
        {
            name: "local_interface",
            type: "string"
        },
        {
            name: "remote_object",
            type: "string"
        },
        {
            name: "expire",
            type: "auto"
        },
        {
            name: "method",
            type: "string"
        },
        {
            name: "remote_interface",
            type: "string"
        }
    ]
});
