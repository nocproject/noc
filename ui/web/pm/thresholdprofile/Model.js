//---------------------------------------------------------------------
// pm.thresholdprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.thresholdprofile.Model");

Ext.define("NOC.pm.thresholdprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/thresholdprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "umbrella_filter_handler",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
