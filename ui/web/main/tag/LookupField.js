//---------------------------------------------------------------------
// NOC.main.tag.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.tag.LookupField");

Ext.define("NOC.main.tag.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.tag.LookupField",
    requires: ["NOC.main.tag.Lookup"]
});
