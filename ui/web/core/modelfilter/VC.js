//---------------------------------------------------------------------
// NOC.core.modelfilter.VC
// VC model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.VC");

Ext.define("NOC.core.modelfilter.VC", {
  extend: "NOC.core.modelfilter.Base",

  initComponent: function(){
    var me = this;

    Ext.apply(this, {
      items: [
        {
          xtype: "numberfield",
          name: me.name,
          fieldLabel: me.title,
          labelAlign: "top",
          itemId: me.name,
          width: me.width,
          listeners: {
            change: {
              scope: me,
              fn: me.onChange,
            },
          },
        },
      ],
    });
    me.callParent();
    me.field = me.getComponent(me.name);
  },

  getFilter: function(){
    var me = this,
      r = {},
      value = me.field.getValue();
    if(value)
      r[this.name + "__vc"] = value;
    return r;
  },

  setFilter: function(){
    console.warn("setting a value for the field VC is not implemented");
  },
});
