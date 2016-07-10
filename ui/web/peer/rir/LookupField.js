//---------------------------------------------------------------------
// NOC.peer.rir.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.rir.LookupField");

Ext.define("NOC.peer.rir.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.peer.rir.LookupField",
    requires: ["NOC.peer.rir.Lookup"]
});
