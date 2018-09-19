//---------------------------------------------------------------------
// phone.phonerange Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonerange.Model");

Ext.define("NOC.phone.phonerange.Model", {
    extend: "Ext.data.Model",
    rest_url: "/phone/phonerange/",

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
            name: "profile__label",
            type: "string",
            persist: false
        },
        {
            name: "state",
            type: "string"
        },
        {
            name: "state__label",
            type: "string",
            persist: false
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "parent",
            type: "string"
        },
        {
            name: "to_number",
            type: "string"
        },
        {
            name: "project",
            type: "int"
        },
        {
            name: "project__label",
            type: "int",
            persist: false
        },
        {
            name: "from_number",
            type: "string"
        },
        {
            name: "supplier",
            type: "string"
        },
        {
            name: "supplier__label",
            type: "string",
            persist: true
        },
        {
            name: "dialplan",
            type: "string"
        },
        {
            name: "dialplan__label",
            type: "string",
            persist: false
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "total_numbers",
            type: "int",
            persist: false
        },
        {
            name: "to_allocate_numbers",
            type: "boolean"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        },
        {
            name: "administrative_domain",
            type: "string"
        },
        {
            name: "administrative_domain__label",
            type: "string",
            persist: false
        },
        {
            name: "static_service_groups",
            type: "auto"
        },
        {
            name: "effective_service_groups",
            type: "auto",
            persist: false
        },
        {
            name: "static_client_groups",
            type: "auto"
        },
        {
            name: "effective_client_groups",
            type: "auto",
            persist: false
        }
    ]
});
