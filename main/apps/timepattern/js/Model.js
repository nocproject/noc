//---------------------------------------------------------------------
// main.timepattern Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.timepattern.Model");

Ext.define("NOC.main.timepattern.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/timepattern/",

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
        }
    ]
});
