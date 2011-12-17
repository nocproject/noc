//---------------------------------------------------------------------
// NOC.fm.mibpreference.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.mibpreference.LookupField");

Ext.define("NOC.fm.mibpreference.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.fm.mibpreference.LookupField",
    requires: ["NOC.fm.mibpreference.Lookup"]
});
