//---------------------------------------------------------------------
// NOC.main.style.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.style.LookupField");

Ext.define("NOC.main.style.LookupField", {
  extend: "NOC.core.ComboBox",
  alias: "widget.main.style.LookupField",
  uiStyle: "medium-combo",

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      listConfig: {
        scope: me,
        getInnerTpl: me.getInnerTpl,
      },
    });
    me.callParent();
  },
  getInnerTpl: function(){
    return "<div style='display:flex; gap:10px;align-items: center;'><div class='noc-color-{id}' style='border: 2px solid; width: 18px; height: 18px;'></div>"
      + "<div>{label}</div>";
  },
});
