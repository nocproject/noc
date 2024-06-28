//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.resourcetemplate.Model");
Ext.define("NOC.sa.resourcetemplate.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/resourcetemplate/",
    actionMethods:{
        read   : 'POST'
    },

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
            name: "resource",
            type: "string"
        },
        {
            name: "fields",
            type: "auto"
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "allow_manual",
            type: "boolean"
        },
        {
            name: "default_state",
            type: "string"
        },
        {
            name: "default_state__label",
            type: "string",
            persist: false
        },
    ]
});
