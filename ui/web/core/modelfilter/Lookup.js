//---------------------------------------------------------------------
// NOC.core.modelfilter.Combo
// Combo lookup model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Lookup");

Ext.define("NOC.core.modelfilter.Lookup", {
  extend: "NOC.core.modelfilter.Base",
  lookup: null, // module.app
  referrer: null, // Referrer application id
  addQuery: true,
  valueName: null, // field name for return value

  initComponent: function(){
    var me = this, className, widget;
    if(me.lookup === "local"){
      widget = Ext.create("Ext.form.field.ComboBox", {
        fieldLabel: me.title,
        labelAlign: "top",
        width: me.width,
        store: me.valuesStore,
        queryMode: "local",
        displayField: "label",
        valueField: "value",
        editable: false,
        listeners: {
          scope: me,
          select: me.onChange,
          clear: me.onChange,
        },
      });
    } else{
      var lookupConfig = {
        fieldLabel: me.title,
        labelAlign: "top",
        width: me.width,
        uiStyle: undefined,
        listeners: {
          scope: me,
          select: me.onChange,
          clear: me.onChange,
        },
      };
      if(me.addQuery){
        lookupConfig.query = {
          "id__referred": me.referrer + "__" + me.name,
        };
      }
      className = "NOC." + me.lookup + ".LookupField";
      widget = Ext.create(className, lookupConfig);
    }
    me.combo = widget;
    Ext.apply(me, {
      items: [widget],
    });
    me.callParent();
  },

  getFilter: function(){
    var me = this,
      v = me.combo.getValue(),
      r = {};
    if(v){
      if(me.valueName){
        r[me.name] = me.combo.getStore().getById(v).get(me.valueName);
      } else{
        r[me.name] = v;
      }
    }
    return r;
  },

  setFilter: function(filter){
    var me = this;
    if(me.name in filter){
      // if(me.valueName) {
      // me.combo.getStore().load({
      //     callback: function() {
      //         var me = this;
      //         console.log('loaded');
      //         me.combo.setValue(me.combo.getStore().findRecord(me.valueName, filter[me.name]));
      //     }
      // });
      // } else {
      me.combo.setValue(filter[me.name]);
      // }
    }
  },
});
