//---------------------------------------------------------------------
// NOC.main.timepattern.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.timepattern.LookupField");

Ext.define("NOC.main.timepattern.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.timepattern.LookupField",
    requires: ["NOC.main.timepattern.Lookup"]
});
