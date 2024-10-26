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
  
  // Constants
  ZOOM_LEVELS: {
    FIT_PAGE: -3,
    FIT_HEIGHT: -1,
    FIT_WIDTH: -2,
  },
  
  MIN_ZOOM: 0.125,
  MAX_ZOOM: 10,
  DEFAULT_ZOOM: -3,
  WHEEL_ZOOM_STEP: 0.01,
  
  // Configuration
  text: __("Fit Page"),
  width: 150,
  zoom: -3.0,
  defaultListenerScope: true,

  // Menu configuration
  menu: {
    xtype: "menu",
    plain: true,
    items: [
      {zoom: -3, text: __("Fit Page"), handler: "setZoom"},
      {zoom: -1, text: __("Fit Height"), handler: "setZoom"},
      {zoom: -2, text: __("Fit Width"), handler: "setZoom"},
      {xtype: "menuseparator"},
      ...Array.from({length: 9}, (_, i) => {
        var zoom = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0][i];
        return {zoom, text: `${zoom * 100}%`, handler: "setZoom"};
      }),
      {xtype: "menuseparator"},
      {
        xtype: "numberfield",
        itemId: "customZoomField",
        fieldLabel: __("Custom Zoom"),
        labelAlign: "top",
        minValue: 10,
        maxValue: 1000,
        value: 100,
        step: 1,
        listeners: {
          change: function(field, newValue){
            var button = field.up("menu").up("button");
            button.setZoom({
              zoom: (newValue || 0) / 100,
              text: `${newValue}%`,
            });
          },
        },
      },
      {xtype: "menuseparator"},
    ],
  },

  // Private methods
  _calculateWheelDelta(event){
    var ratio = window.devicePixelRatio,
      pxFactor;

    switch(true){
      case ratio === 0:
        pxFactor = 1;
        break;
      case Ext.isLinux && Ext.isChrome:
        pxFactor = ratio;
        break;
      case Ext.isMac:
        pxFactor = ratio * 3;
        break;
      default:
        pxFactor = 2 * ratio;
    }
    
    if(event.deltaY){
      switch(event.deltaMode){
        case 0: // DOM_DELTA_PIXEL
          return -event.deltaY / pxFactor;
        case 1: // DOM_DELTA_LINE
          return -event.deltaY * 20;
        case 2: // DOM_DELTA_PAGE
          return -event.deltaY * 60;
      }
    }
    
    if(event.deltaX || event.deltaZ) return 0;
    if(event.wheelDelta) return (event.wheelDeltaY || event.wheelDelta) / 2;
    if(event.detail){
      return Math.abs(event.detail) < 32765 ? 
        -event.detail * 20 : 
        event.detail / -32765 * 60;
    }
    return 0;
  },

  _getSvgElement(){
    var container = this.up("filescheme, vizscheme").down("#schemeContainer");
    return container.getEl().dom.querySelector("svg");
  },

  _updateCustomField(scale){
    var customZoomField = this.menu.down("#customZoomField");
    if(customZoomField){
      customZoomField.setValue(Math.round(scale * 100));
    }
  },

  // Public methods
  fitSvgToContainer(element){
    var container = element.parentNode,
      containerAspectRatio = container.clientWidth / container.clientHeight,
      svgAspectRatio = element.viewBox.baseVal.width / element.viewBox.baseVal.height,
      attributes = {
        height: "100%",
        width: "100%",
        preserveAspectRatio: "xMinYMin meet",
        "object-fit": "contain",
        style: containerAspectRatio > svgAspectRatio ?
          "width: auto; height: 100%;" :
          "width: 100%; height: auto;",
      };

    Object.entries(attributes).forEach(([key, value]) => 
      element.setAttribute(key, value),
    );
    this._updateCustomField(1.0);
    this.zoom = 1.0;
  },

  getZoom(){
    return this.zoom > 0 ? this.zoom : 1;
  },

  onWheel(event){
    event.preventDefault();
    var scale = this.getZoom(),
      delta = this._calculateWheelDelta(event),
      newScale = Math.min(
        Math.max(this.MIN_ZOOM, scale + delta * -this.WHEEL_ZOOM_STEP),
        this.MAX_ZOOM,
      );
    
    this.setZoomByValue(newScale);
  },

  reset(){
    this.setZoom({zoom: this.ZOOM_LEVELS.FIT_PAGE, text: __("Fit Page")});
  },

  restoreZoom(){
    var zoomText = this.zoom > 0 ? 
      `${Math.round(this.zoom * 100)}%` :
      this.zoom === this.ZOOM_LEVELS.FIT_HEIGHT ? __("Fit Height") :
      this.zoom === this.ZOOM_LEVELS.FIT_WIDTH ? __("Fit Width") :
      this.zoom === this.ZOOM_LEVELS.FIT_PAGE ? __("Fit Page") :
      __("Fit Page");

    this.setZoom({zoom: this.zoom, text: zoomText});
  },

  setScale(element, scale){
    var isWidthAuto = element.style.width === "auto",
      isHeightAuto = element.style.height === "auto",
      style = isWidthAuto ? 
        `width: auto; height: ${100 * scale}%` :
        isHeightAuto ?
          `height: auto; width: ${100 * scale}%` :
          null;
                 
    if(style) element.setAttribute("style", style);
  },

  setZoom(item){
    var element = this._getSvgElement();
    if(!element) return;

    const{zoom: scale, text} = item;
    this.zoom = scale;
    this.setText(text);

    if(scale > 0){
      this.setScale(element, scale);
      return;
    }

    switch(scale){
      case this.ZOOM_LEVELS.FIT_PAGE:
        this.fitSvgToContainer(element);
        break;
      case this.ZOOM_LEVELS.FIT_HEIGHT:
        element.setAttribute("style", "height: 100%; width: auto;");
        break;
      case this.ZOOM_LEVELS.FIT_WIDTH:
        element.setAttribute("style", "height: auto; width: 100%;");
        break;
    }
  },
  
  setZoomByValue(scale){
    var element = this._getSvgElement();
    if(!element) return;

    this.zoom = scale;
    this.setText(`${Math.round(scale * 100)}%`);
    this._updateCustomField(scale);
    this.setScale(element, scale);
  },
});