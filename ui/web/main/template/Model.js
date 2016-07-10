//---------------------------------------------------------------------
// main.template Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.template.Model");

Ext.define("NOC.main.template.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/template/",

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
            name: "subject",
            type: "string"
        },
        {
            name: "body",
            type: "string"
        }
    ]
});
