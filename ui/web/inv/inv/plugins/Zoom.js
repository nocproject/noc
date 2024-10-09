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
  store: {
    fields: [
      {name: "zoom", type: "float"},
      {name: "label", type: 'string'},
    ],
    data: [
      {zoom: 0, label: __("Max Height")},
      {zoom: 0, label: __("Max Width")},
      {zoom: 0.25, label: "25%"},
      {zoom: 0.5, label: "50%"},
      {zoom: 0.75, label: "75%"},
      {zoom: 1.0, label: "100%"},
      {zoom: 1.25, label: "125%"},
      {zoom: 1.5, label: "150%"},
      {zoom: 2.0, label: "200%"},
      {zoom: 3.0, label: "300%"},
      {zoom: 4.0, label: "400%"},
    ],
  },
  defaultListenerScope: true,
  width: 150,
  value: 1.0,
  valueField: "zoom",
  displayField: "label",
  editable: false,
  listeners: {
    select: "setZoom",
  },
  setZoom: function(combo){
    var svgDoc = undefined,
      me = this.up("#" + this.appPanel),
      img = me.down("#scheme"),
      scale = combo.getValue(),
      imgEl = img.getEl().dom,
      container = img.up();
    svgDoc = imgEl.querySelector("svg");
    if(!svgDoc && imgEl.querySelector("object").contentDocument){
      svgDoc = imgEl.querySelector("object").contentDocument.querySelector("svg");
    }
    imgEl.style.transformOrigin = "0 0";
    imgEl.style.transform = "none";
    if(svgDoc){
      var record,
        schemaSize = svgDoc.getBoundingClientRect(),
        store = this.getStore();
      if(this.getRawValue() === __("Max Height")){
        scale = container.getHeight() / schemaSize.height;
        record = store.findRecord("label", __("Max Height"));
        record.set("zoom", scale)
        this.setValue(scale);
      } else if(this.getRawValue() === __("Max Width")){
        scale = container.getWidth() / schemaSize.width;
        record = store.findRecord("label", __("Max Width"));
        record.set("zoom", scale)
        this.setValue(scale);
      }
      store.commitChanges();
    }
    imgEl.style.transform = "scale(" + scale + ")";
  },
  restoreZoom: function(){
    this.setZoom(this);
  },
});
