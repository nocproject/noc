//---------------------------------------------------------------------
// NOC.inv.interface.type.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.type.LookupField");

Ext.define("NOC.inv.interface.type.LookupField", {
  extend: "Ext.form.ComboBox",
  alias: "widget.inv.interface.TypeLookupField",
  queryMode: "local",
  valueField: "value",
  displayField: "label",
  store: {
    data: [
      {value: "physical", label: __("Physical")},
      {value: "SVI", label: __("SVI")},
      {value: "aggregated", label: __("Aggregated")},
      {value: "loopback", label: __("Loopback")},
    ],
  },
  triggers: {
    clear: {
      cls: "x-form-clean-trigger",
      hidden: true,
      weight: -1,
      handler: function(field){
        field.setValue(null);
        field.fireEvent("select", field);
      },
    },
  },
  listeners: {
    change: function(field, value){
      this.showTriggers(value);
    },
  },

  initComponent: function(){
    var me = this;

    me.showTriggers(null);
    this.callParent();
  },
  showTriggers: function(value){
    this.getTrigger("clear").show();
    if(value == null || value === ""){
      this.getTrigger("clear").hide();
    }
  },
});
