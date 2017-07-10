//---------------------------------------------------------------------
// main.remotesystem Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.remotesystem.Model");

Ext.define("NOC.main.remotesystem.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/remotesystem/",

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
            name: "name",
            type: "string"
        },
        {
            name: "handler",
            type: "string"
        },
        {
            name: "environment",
            type: "auto"
        },

        {
            name: "enable_admdiv",
            type: "boolean"
        },

        {
            name: "enable_administrativedomain",
            type: "boolean"
        },
        {
            name: "enable_authprofile",
            type: "boolean"
        },
        {
            name: "enable_container",
            type: "boolean"
        },
        {
            name: "enable_link",
            type: "boolean"
        },
        {
            name: "enable_managedobject",
            type: "boolean"
        },
        {
            name: "enable_managedobjectprofile",
            type: "boolean"
        },
        {
            name: "enable_networksegment",
            type: "boolean"
        },
        {
            name: "enable_service",
            type: "boolean"
        },
        {
            name: "enable_subscriber",
            type: "boolean"
        },
        {
            name: "enable_terminationgroup",
            type: "boolean"
        },
        {
            name: "enable_ttsystem",
            type: "boolean"
        }
    ]
});
