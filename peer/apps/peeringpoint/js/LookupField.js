//---------------------------------------------------------------------
// NOC.peer.peeringpoint.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.peeringpoint.LookupField");

Ext.define("NOC.peer.peeringpoint.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.peer.peeringpoint.LookupField",
    requires: ["NOC.peer.peeringpoint.Lookup"]
});
