//---------------------------------------------------------------------
// sla.slaprobe Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sla.slaprobe.Model");

Ext.define("NOC.sla.slaprobe.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sla/slaprobe/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "profile",
            type: "string"
        },
        {
            name: "profile__label",
            type: "string",
            persist: false
        },
        {
            name: "tests",
            type: "auto"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "managed_object",
            type: "int"
        },
        {
            name: "managed_object__label",
            type: "string",
            persist: false
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
