//---------------------------------------------------------------------
// sa.terminationgroup Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.terminationgroup.Model");

Ext.define("NOC.sa.terminationgroup.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/terminationgroup/",

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
            name: "terminators",
            type: "auto",
            persist: false
        },
        {
            name: "n_access",
            type: "integer",
            persist: false
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "remote_system__label",
            type: "string",
            persist: false
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
        {
            name: "tags",
            type: "auto"
        }
    ]
});
