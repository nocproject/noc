//---------------------------------------------------------------------
// crm.supplier Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.supplier.Model");

Ext.define("NOC.crm.supplier.Model", {
    extend: "Ext.data.Model",
    rest_url: "/crm/supplier/",

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
            name: "tags",
            type: "auto"
        },
        {
            name: "is_affilated",
            type: "boolean"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
