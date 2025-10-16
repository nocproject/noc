//---------------------------------------------------------------------
// NOC.core.modelfilter.Combo
// VC Filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.VCFilter");

Ext.define("NOC.core.modelfilter.VCFilter", {
  extend: "NOC.core.modelfilter.Base",
  referrer: null, // Referrer application id

  initComponent: function(){
    var me = this,
      w = Ext.create("NOC.vc.vcfilter.LookupField", {
        width: me.width,
        fieldLabel: me.title,
        labelAlign: "top",
        listeners: {
          select: {
            scope: me,
            fn: me.onChange,
          },
        },
      });

    Ext.apply(me, {items: [w]});
    me.callParent();
    me.combo = w;
  },

  getFilter: function(){
    var me = this,
      v = me.combo.getValue(),
      r = {};
    if(v)
      r[me.name + "__vcfilter"] = v;
    return r;
  },

  setFilter: function(){
    console.warn("setting a value for the field VCFilter is not implemented");
  },
});
