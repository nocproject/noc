//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.monitor.Model");
Ext.define("NOC.sa.monitor.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/monitor/",
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
            name: "address",
            type: "string"
        },
        {
            name: "profile_name",
            type: "string"
        },
        {
            name: "b_time_start",
            type: "string"
        },
        {
            name: "b_last_success",
            type: "string"
        },
        {
            name: "b_status",
            type: "string"
        },
        {
            name: "b_last_status",
            type: "string"
        },
        {
            name: "b_duration",
            type: "string"
        },
        {
            name: "b_time",
            type: "string"
        },
        {
            name: "p_time_start",
            type: "string"
        },
        {
            name: "p_last_success",
            type: "string"
        },
        {
            name: "p_status",
            type: "string"
        },
        {
            name: "p_last_status",
            type: "string"
        },
        {
            name: "p_duration",
            type: "string"
        },
        {
            name: "p_time",
            type: "string"
        },
        {
            name: "in_progress",
            type: "boolean"
        }
    ]
});
