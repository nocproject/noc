//---------------------------------------------------------------------
// project.project Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.project.project.Model");

Ext.define("NOC.project.project.Model", {
    extend: "Ext.data.Model",
    rest_url: "/project/project/",

    fields: [
        {
            name: "id",
            type: "int"
        },
        {
            name: "code",
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
