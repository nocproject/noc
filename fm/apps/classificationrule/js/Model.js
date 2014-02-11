//---------------------------------------------------------------------
// fm.classificationrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.classificationrule.Model");

Ext.define("NOC.fm.classificationrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/classificationrule/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "vars",
            type: "auto"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "patterns",
            type: "auto"
        },
        {
            name: "preference",
            type: "int",
            defaultValue: 1000
        },
        {
            name: "uuid",
            type: "string"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "event_class",
            type: "string"
        },
        {
            name: "event_class__label",
            type: "string",
            persist: false
        },
        {
            name: "datasources",
            type: "auto"
        }
    ]
});
