//---------------------------------------------------------------------
// NOC.fm.oidalias.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.oidalias.LookupField");

Ext.define("NOC.fm.oidalias.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.fm.oidalias.LookupField",
    requires: ["NOC.fm.oidalias.Lookup"]
});
