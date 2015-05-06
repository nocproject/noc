//---------------------------------------------------------------------
// fm.ignorepattern Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.ignorepattern.Model");

Ext.define("NOC.fm.ignorepattern.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/ignorepattern/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "pattern",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "source",
            type: "string"
        }
    ]
});
