//---------------------------------------------------------------------
// crm.subscriber Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.subscriber.Model");

Ext.define("NOC.crm.subscriber.Model", {
    extend: "Ext.data.Model",
    rest_url: "/crm/subscriber/",

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
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "tags",
            type: "auto"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
