//---------------------------------------------------------------------
// main.pyrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pyrule.Model");

Ext.define("NOC.main.pyrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/pyrule/",

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
            name: "full_name",
            type: "string",
            persist: false
        },
        {
            name: "source",
            type: "string"
        },
        {
            name: "last_changed",
            type: "date"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
