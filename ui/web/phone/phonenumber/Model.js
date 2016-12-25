//---------------------------------------------------------------------
// phone.phonenumber Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonenumber.Model");

Ext.define("NOC.phone.phonenumber.Model", {
    extend: "Ext.data.Model",
    rest_url: "/phone/phonenumber/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "profile",
            type: "string"
        },
        {
            name: "category",
            type: "string"
        },
        {
            name: "protocol",
            type: "string",
            defaultValue: "SIP"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "service",
            type: "string"
        },
        {
            name: "changed",
            type: "auto"
        },
        {
            name: "number",
            type: "string"
        },
        {
            name: "project",
            type: "int"
        },
        {
            name: "status",
            type: "string",
            defaultValue: "N"
        },
        {
            name: "allocated_till",
            type: "auto"
        },
        {
            name: "phone_range",
            type: "string"
        },
        {
            name: "dialplan",
            type: "string"
        }
    ]
});
