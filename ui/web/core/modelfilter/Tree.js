//---------------------------------------------------------------------
// NOC.core.modelfilter.Combo
// Combo lookup model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Tree");

Ext.define("NOC.core.modelfilter.Tree", {
  extend: "NOC.core.modelfilter.Base",
  lookup: null, // module.app
  referrer: null, // Referrer application id

  initComponent: function(){
    var me = this,
      wn = "NOC." + me.lookup + ".TreeCombo";
    me.tree = Ext.create(wn, {
      labelAlign: "top",
      fieldLabel: me.title,
      width: me.width,
      restUrl: "/" + me.lookup.replace(".", "/"),
      listeners: {
        scope: me,
        clear: me.onChange,
        select: me.onChange,
        change: me.onChange,
      },
    });
    Ext.apply(me, {
      items: [me.tree],
    });
    me.callParent();
  },

  getFilter: function(){
    var me = this,
      r = {},
      v;
    if(me.tree.fieldValue){
      v = me.tree.getFieldValue().id;
      if(v){
        if(v === "_root_"){
          r[me.name + "__exists"] = false;
        } else{
          r[me.name] = v;
        }
      }
      return r;
    }
    return r;
  },

  setFilter: function(filter){
    var me = this;
    if(me.name in filter){
      me.tree.restoreById(filter[me.name]);
    } else{
      if(me.name + "__exists" in filter){
        me.tree.restoreById("_root_");
      }
    }
  },
});
