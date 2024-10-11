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
      container = img.up("#schemeContainer");
    svgDoc = imgEl.querySelector("svg");
    if(!svgDoc && imgEl.querySelector("object").contentDocument){
      svgDoc = imgEl.querySelector("object").contentDocument.querySelector("svg");
    }
    // console.log(this._getSvgDoc(). svgDoc);
    if(svgDoc){
      var schemaSize = svgDoc.getBoundingClientRect();
      svgDoc.style.transformOrigin = "0 0";
      svgDoc.style.transform = "none";
      if(this.getRawValue() === __("Max Height")){
        scale = container.getHeight() / schemaSize.height;
        this._updateValue(scale, this.getRawValue());
      } else if(this.getRawValue() === __("Max Width")){
        scale = container.getWidth() / schemaSize.width;
        this._updateValue(scale, this.getRawValue());
      }
    }
    // imgEl.style.width = container.getWidth() + 'px';
    // imgEl.style.height = container.getHeight() + 'px';
    // imgEl.style.objectFit = 'contain'; // или 'cover' в зависимости от нужного эффекта
    console.log(`container : ${container.getWidth()}x${container.getHeight()}`);
    if(svgDoc){
      svgDoc.style.transform = "scale(" + scale + ")";
      // var scheme = svgDoc.getBoundingClientRect(),
      //   schemeBB = svgDoc.getBBox();
      // img.setHeight(scheme.height);
      // img.setWidth(scheme.width);
      // console.log(`scheme : ${scheme.width}x${scheme.height}`);
      // console.log(`schemeBB : ${schemeBB.width}x${schemeBB.height}`);
    } else{
      console.log("SVG not found");
      // imgEl.style.transformOrigin = "0 0";
      // imgEl.style.transform = "none";
      // imgEl.style.transform = "scale(" + scale + ")";
    }
  },
  restoreZoom: function(){
    this.setZoom(this);
  },
  _updateValue: function(zoom, label){
    var store = this.getStore(),
      record = store.findRecord("label", label);
    record.set("zoom", zoom);
    store.commitChanges();
    this.setValue(zoom);
  },
  _getSvgDoc: function(){
    var me = this.up("#" + this.appPanel),
      scheme = me.down("#scheme"),
      schemeEl = scheme.getEl().dom,
      svgDoc = schemeEl.querySelector("svg");
    if(Ext.isEmpty(svgDoc)){
      return schemeEl.querySelector("object").contentDocument.querySelector("svg");
    }
    return svgDoc;
  },
  _getScale: function(svgDoc){
    var scale = 1.0;
    return scale;
  },
});
