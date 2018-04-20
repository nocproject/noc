//---------------------------------------------------------------------
// NOC.peer.communitytype.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.communitytype.LookupField");

Ext.define("NOC.peer.communitytype.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.peer.communitytype.LookupField",
    requires: ["NOC.peer.communitytype.Lookup"]
});
