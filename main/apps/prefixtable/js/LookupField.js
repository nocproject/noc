//---------------------------------------------------------------------
// NOC.main.prefixtable.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.prefixtable.LookupField");

Ext.define("NOC.main.prefixtable.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.prefixtable.LookupField",
    requires: ["NOC.main.prefixtable.Lookup"],
    uiStyle: "medium"
});
