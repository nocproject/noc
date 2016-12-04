//---------------------------------------------------------------------
// sla.slaprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sla.slaprofile.Model");

Ext.define("NOC.sla.slaprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sla/slaprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "metrics",
            type: "auto"
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
            name: "style",
            type: "string"
        },
        {
            name: "style__label",
            type: "string",
            persist: false
        }
    ]
});
