//---------------------------------------------------------------------
// NOC.{{module}}.{{app}}.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-{{year}} The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.{{module}}.{{app}}.LookupField");

Ext.define("NOC.{{module}}.{{app}}.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.{{module}}.{{app}}.LookupField",
    requires: ["NOC.{{module}}.{{app}}.Lookup"]
});
