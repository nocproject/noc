//---------------------------------------------------------------------
// main.prefixtable Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.prefixtable.PrefixModel");

Ext.define("NOC.main.prefixtable.PrefixModel", {
    extend: "Ext.data.Model",
    rest_url: "/main/prefixtable/{{parent}}/prefixes/",
    parentField: "table_id",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "afi",
            type: "string"
        },
        {
            name: "prefix",
            type: "string"
        },
    ]
});
