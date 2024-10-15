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
      {zoom: -3, label: __("Zoom to Fit")},
      {zoom: -1, label: __("Zoom to Height")},
      {zoom: -2, label: __("Zoom to Width")},
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
  setZoom: function(combo, record){
    var {element, bb} = this._getSvgElement(),
      scale = record.get("zoom");
    element.removeAttribute("width");
    element.removeAttribute("height");
    element.removeAttribute("style");
    if(record.get("zoom") === 1.0){
      this.fitSvgToContainer();
      return;
    }
    if(record.get("zoom") === -1){ // Zoom to Height 
      if(bb.height > bb.width){// h > w 
        element.setAttribute("style", "height: 100%;width: auto;max-width: none;max-height: 100%;");
      } else{ // w > h 
        element.setAttribute("style", "height: 100%;width: auto;max-width: none;max-height: 100%;");
      }
      return;
    }
    if(record.get("zoom") === -2){ // Zoom to Width
      if(bb.height > bb.width){ // h > w
        element.setAttribute("style", "width: 100%;height: auto;max-height: none;max-width: 100%;");
      } else{ // w > h
        element.setAttribute("style", "width: 100%;height: auto;max-height: none;max-width: 100%;");
      }
      return;
    }
    if(record.get("zoom") === -3){ // Zoom to Fit
      this.fitSvgToContainer();
      return;
    }
    if(bb.height > bb.width){// h > w 
      element.setAttribute("style", `width: auto;height: ${100 * scale}%`);
    } else{ // w > h
      element.setAttribute("style", `height: auto;width: ${100 * scale}%`);
    }
  },
  fitSvgToContainer: function(){
    var {element} = this._getSvgElement();
    element.setAttribute("height", "100%");
    element.setAttribute("width", "100%");
    element.setAttribute("preserveAspectRatio", "xMinYMin meet");
    element.setAttribute("object-fit", "contain");
    element.setAttribute("style", "transform: scale(1);transform-origin: center center;");
  },
  restoreZoom: function(){
    var store = this.getStore(),
      record = store.findRecord("zoom", this.getValue());
    this.setZoom(this, record);
  },
  _updateValue: function(zoom, label){
    var store = this.getStore(),
      record = store.findRecord("label", label);
    record.set("zoom", zoom);
    store.commitChanges();
    this.setValue(zoom);
  },
  _getSvgElement: function(){
    var container = this.up("panel").down("#schemeContainer"),
      svgElement = container.getEl().dom.querySelector("svg");
    if(svgElement){
      return {
        element: svgElement,
        bb: svgElement.getBBox(),
      }
    }
  },
});
