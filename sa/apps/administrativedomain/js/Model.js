//---------------------------------------------------------------------
// sa.administrativedomain Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.administrativedomain.Model");

Ext.define("NOC.sa.administrativedomain.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/administrativedomain/",

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
            name: "description",
            type: "string"
        },
        {
            name: "object_count",
            type: "int",
            persist: false
        }
    ]
});
