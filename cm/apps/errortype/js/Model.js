//---------------------------------------------------------------------
// cm.errortype Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.errortype.Model");

Ext.define("NOC.cm.errortype.Model", {
    extend: "Ext.data.Model",
    rest_url: "/cm/errortype/",

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
            name: "body_template",
            type: "string"
        },
        {
            name: "subject_template",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "uuid",
            type: "string"
        }
    ]
});
