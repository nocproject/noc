//---------------------------------------------------------------------
// NOC.cm.errortype.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.errortype.LookupField");

Ext.define("NOC.cm.errortype.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.cm.errortype.LookupField",
    requires: ["NOC.cm.errortype.Lookup"]
});
