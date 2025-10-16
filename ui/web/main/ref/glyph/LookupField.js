//---------------------------------------------------------------------
// NOC.main.ref.glyph.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.ref.glyph.LookupField");

Ext.define("NOC.main.ref.glyph.LookupField", {
  extend: "NOC.core.ComboBox",
  alias: "widget.main.ref.glyph.LookupField",
  tpl: '<tpl for="."><div class="x-boundlist-item"><i class="{id}"></i> {label}</div></tpl>',
  uiStyle: "medium-combo",

  cleanValue: function(record){
    var me = this,
      rv = record.get(me.name),
      mv = {};
    if(rv === "" || rv === 0){
      return ""
    }
    mv[me.valueField] = rv;
    mv[me.displayField] = rv.split(/\s/)[1].replace("fa-","");
    return me.store.getModel().create(mv);
  },
});
