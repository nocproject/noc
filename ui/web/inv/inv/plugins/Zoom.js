//---------------------------------------------------------------------
// inv.inv.plugins.Zoom widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.Zoom");

Ext.define("NOC.inv.inv.plugins.Zoom", {
  extend: "Ext.button.Button",
  alias: "widget.invPluginsZoom",
  text: __("Fit Page"),
  menu: {
    xtype: "menu",
    plain: true,
    items: [
      {zoom: -3, text: __("Fit Page"), handler: "setZoom"},
      {zoom: -1, text: __("Fit Height"), handler: "setZoom"},
      {zoom: -2, text: __("Fit Width"), handler: "setZoom"},
      {xtype: "menuseparator"},
      {zoom: 0.25, text: "25%", handler: "setZoom"},
      {zoom: 0.5, text: "50%", handler: "setZoom"},
      {zoom: 0.75, text: "75%", handler: "setZoom"},
      {zoom: 1.0, text: "100%", handler: "setZoom"},
      {zoom: 1.25, text: "125%", handler: "setZoom"},
      {zoom: 1.5, text: "150%", handler: "setZoom"},
      {zoom: 2.0, text: "200%", handler: "setZoom"},
      {zoom: 3.0, text: "300%", handler: "setZoom"},
      {zoom: 4.0, text: "400%", handler: "setZoom"},
      {xtype: "menuseparator"},
      {
        xtype: "numberfield",
        fieldLabel: __("Custom Zoom"),
        labelAlign: "top",
        minValue: 10,
        maxValue: 500,
        value: 100,
        step: 1,
        listeners: {
          change: function(field, newValue){
            var button = field.up("menu").up("button");
            button.setZoom({zoom: (newValue || 0) / 100, text: newValue + "%"});
          },
        },
      },
      {xtype: "menuseparator"},
    ],
  },
  defaultListenerScope: true,
  width: 150,
  zoom: -3.0,
  setZoomByValue: function(scale){
    var {element, bb} = this._getSvgElement();
    if(element === null){
      return;
    }
    if(bb.height > bb.width){// h > w 
      element.setAttribute("style", `width: auto;height: ${100 * scale}%`);
    } else{ // w > h
      element.setAttribute("style", `height: auto;width: ${100 * scale}%`);
    }
    this.zoom = scale;
    this.setText(Math.round(scale * 100) + "%");
  },
  getZoom: function(){
    if(this.zoom > 0){
      return this.zoom;
    }
    return 1;
  },
  setZoom: function(item){
    var customZoomField,
      {element, bb} = this._getSvgElement(),
      scale = item.zoom;
    if(element === null){
      return;
    }
    this.zoom = scale;
    this.setText(item.text);
    element.removeAttribute("width");
    element.removeAttribute("height");
    element.removeAttribute("style");
    if(scale === 1.0){
      this.fitSvgToContainer();
      return;
    }
    if(scale === -1){ // Zoom to Height 
      element.setAttribute("style", "height: 100%;width: auto;max-width: none;max-height: 100%;");
      return;
    }
    if(scale === -2){ // Zoom to Width
      element.setAttribute("style", "width: 100%;height: auto;max-height: none;max-width: 100%;");
      return;
    }
    if(scale === -3){ // Zoom to Fit
      this.fitSvgToContainer();
      return;
    }
    if(bb.height > bb.width){// h > w 
      element.setAttribute("style", `width: auto;height: ${100 * scale}%`);
    } else{ // w > h
      element.setAttribute("style", `height: auto;width: ${100 * scale}%`);
    }
    customZoomField = this.menu.query("numberfield")[0];
    if(customZoomField){
      customZoomField.setValue(Math.round(scale * 100));
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
  reset: function(){
    this.setZoom({zoom: -3.0, text: __("Fit Page")});
  },
  restoreZoom: function(){
    var text = __("Fit Page");
    if(this.zoom > 0){
      var scale = Math.round(this.zoom * 100);
      text = `${scale}%`;
    } else if(this.zoom === -1){
      text = __("Fit Height");
    } else if(this.zoom === -2){
      text = __("Fit Width");
    }
    this.setZoom({zoom: this.zoom, text: text});
  },
  _getSvgElement: function(){
    var container = this.up("filescheme, vizscheme").down("#schemeContainer"),
      svgElement = container.getEl().dom.querySelector("svg");
    if(svgElement){
      return {
        element: svgElement,
        bb: svgElement.getBBox(),
      }
    } else{
      return {
        element: null,
        bb: null,
      };
    }
  },
  onWheel: function(event){
    event.preventDefault();
    var scale = this.getZoom(),
      delta = this.getWheelDelta(event);
    scale += delta * -0.01;
    scale = Math.min(Math.max(0.125, scale), 6);
    this.setZoomByValue(scale);
  },
  getWheelPxFactor: function(){
    var ratio = window.devicePixelRatio;
    return Ext.isLinux && Ext.isChrome ? ratio :
      Ext.isMac ? ratio * 3 :
      ratio > 0 ? 2 * ratio : 1;
  },
  getWheelDelta: function(e){
    return (e.deltaY && e.deltaMode === 0) ? -e.deltaY / this.getWheelPxFactor() : 
      (e.deltaY && e.deltaMode === 1) ? -e.deltaY * 20 :
      (e.deltaY && e.deltaMode === 2) ? -e.deltaY * 60 :
      (e.deltaX || e.deltaZ) ? 0 :
      e.wheelDelta ? (e.wheelDeltaY || e.wheelDelta) / 2 :
      (e.detail && Math.abs(e.detail) < 32765) ? -e.detail * 20 :
      e.detail ? e.detail / -32765 * 60 :
      0;
  },
});
