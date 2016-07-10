//---------------------------------------------------------------------
// main.timepattern TermModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.timepattern.TermModel");

Ext.define("NOC.main.timepattern.TermModel", {
    extend: "Ext.data.Model",
    rest_url: "/main/timepattern/{{parent}}/terms/",
    parentField: "time_pattern_id",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "term",
            type: "string"
        }
    ]
});
