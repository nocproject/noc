//---------------------------------------------------------------------
// NOC.peer.peer.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.peer.LookupField");

Ext.define("NOC.peer.peer.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.peer.peer.LookupField",
    requires: ["NOC.peer.peer.Lookup"]
});
