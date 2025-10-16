//---------------------------------------------------------------------
// NOC.main.style.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
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
    return "<div class='noc-color-{id}'>{label}</div>";
  },
});
