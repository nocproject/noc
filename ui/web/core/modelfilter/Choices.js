//---------------------------------------------------------------------
// NOC.core.modelfilter.Choices
// Boolean model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Choices");

Ext.define("NOC.core.modelfilter.Choices", {
  extend: "NOC.core.modelfilter.Base",

  initComponent: function(){
    var me = this;

    me.combo = Ext.create("Ext.form.field.ComboBox", {
      fieldLabel: me.title,
      labelAlign: "top",
      width: me.width,
      store: me.store,
      listeners: {
        scope: me,
        select: me.onChange,
        specialkey: me.onSpecialKey,
      },
    });

    Ext.apply(me, {
      items: [me.combo],
    });
    me.callParent();
  },

  getFilter: function(){
    var me = this,
      v = me.combo.getValue(),
      r = {};
    if(v){
      r[me.name] = v;
    }
    return r;
  },

  setFilter: function(filter){
    var me = this;
    if(me.name in filter){
      me.combo.setValue(filter[me.name]);
    }
  },

  onSpecialKey: function(field, e){
    var me = this;
    switch(e.keyCode){
      case e.ESC:
        me.combo.clearValue();
        me.onChange();
        break;
    }
  },
});
