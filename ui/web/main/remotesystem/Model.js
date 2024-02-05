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
            name: "enable_address",
            type: "boolean"
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
            name: "enable_building",
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
            name: "enable_networksegmentprofile",
            type: "boolean"
        },
        {
            name: "enable_object",
            type: "boolean"
        },
        {
            name: "enable_sensor",
            type: "boolean"
        },
        {
            name: "enable_service",
            type: "boolean"
        },
        {
            name: "enable_serviceprofile",
            type: "boolean"
        },
        {
            name: "enable_subscriber",
            type: "boolean"
        },
        {
            name: "enable_subscriberprofile",
            type: "boolean"
        },
        {
            name: "enable_resourcegroup",
            type: "boolean"
        },
        {
            name: "enable_ttsystem",
            type: "boolean"
        },
        {
            name: "enable_l2domain",
            type: "boolean"
        },
        {
            name: "enable_project",
            type: "boolean"
        },
        {
            name: "enable_label",
            type: "boolean"
        },
        {
            name: "enable_discoveredobject",
            type: "boolean"
        },
        {
            name: "enable_street",
            type: "boolean"
        }
    ]
});
