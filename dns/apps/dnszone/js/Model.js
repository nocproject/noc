//---------------------------------------------------------------------
// dns.dnszone Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnszone.Model");

Ext.define("NOC.dns.dnszone.Model", {
    extend: "Ext.data.Model",
    rest_url: "/dns/dnszone/",

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
            name: "is_auto_generated",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "serial",
            type: "int",
            defaultValue: 0
        },
        {
            name: "profile",
            type: "int"
        },
        {
            name: "profile__label",
            type: "string",
            persist: false
        },
        {
            name: "project",
            type: "int"
        },
        {
            name: "project__label",
            type: "string",
            persist: false
        },
        {
            name: "notification_group",
            type: "int"
        },
        {
            name: "notification_group__label",
            type: "string",
            persist: false
        },
        {
            name: "paid_till",
            type: "date"
        },
        {
            name: "tags",
            type: "auto"
        }
    ]
});
