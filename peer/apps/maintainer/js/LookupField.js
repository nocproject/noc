//---------------------------------------------------------------------
// NOC.peer.maintainer.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.maintainer.LookupField");

Ext.define("NOC.peer.maintainer.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.peer.maintainer.LookupField",
    requires: ["NOC.peer.maintainer.Lookup"]
});
