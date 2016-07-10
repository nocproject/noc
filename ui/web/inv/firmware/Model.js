//---------------------------------------------------------------------
// inv.firmware Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.firmware.Model");

Ext.define("NOC.inv.firmware.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/firmware/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "vendor",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "download_url",
            type: "string"
        },
        {
            name: "version",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
