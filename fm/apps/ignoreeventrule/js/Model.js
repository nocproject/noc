//---------------------------------------------------------------------
// fm.ignoreeventrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.ignoreeventrule.Model");

Ext.define("NOC.fm.ignoreeventrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/ignoreeventrule/",

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
            name: "left_re",
            type: "string"
        },
        {
            name: "right_re",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
