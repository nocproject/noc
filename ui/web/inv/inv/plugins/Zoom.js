//---------------------------------------------------------------------
// inv.inv.plugins.Zoom widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.Zoom");

Ext.define("NOC.inv.inv.plugins.Zoom", {
  extend: "Ext.form.field.ComboBox",
  alias: "widget.invPluginsZoom",
  store: [
    [0.25, "25%"],
    [0.5, "50%"],
    [0.75, "75%"],
    [1.0, "100%"],
    [1.25, "125%"],
    [1.5, "150%"],
    [2.0, "200%"],
    [3.0, "300%"],
    [4.0, "400%"],
  ],
  defaultListenerScope: true,
  width: 100,
  value: 1.0,
  valueField: "zoom",
  displayField: "label",
  editable: false,
  listeners: {
    select: "setZoom",
  },
  setZoom: function(combo){
    var me = this.up("#" + this.appPanel), 
      img = me.down("#scheme"),
      imgEl = img.getEl().dom;
    imgEl.style.transformOrigin = "0 0";
    imgEl.style.transform = "scale(" + combo.getValue() + ")";
  },
  restoreZoom: function(){
    this.setZoom(this);
  },
});
