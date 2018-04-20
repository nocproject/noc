//---------------------------------------------------------------------
// NOC.peer.community.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.community.LookupField");

Ext.define("NOC.peer.community.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.peer.community.LookupField",
    requires: ["NOC.peer.community.Lookup"]
});
