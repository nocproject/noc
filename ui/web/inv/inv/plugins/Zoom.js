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
  defaultListenerScope: true,
  bind: {
    zoom: "{zoom}",
    text: "{buttonText}",
  },
  viewModel: {
    data: {
      zoom: -3.0,
    },
    formulas: {
      buttonText: {
        bind: {
          bindTo: "{zoom}",
        },
        get: function(zoom){
          return zoom === -3 ? __("Fit Page") :
            zoom === -1 ? __("Fit Height") :
            zoom === -2 ? __("Fit Width") : `${zoom}%`;
        },
      },
      customField: {
        bind: {
          bindTo: "{zoom}",
        },
        get: function(zoom){
          return zoom > 0 ? zoom : 100;
        },
      },
    },
  },
  // Menu configuration
  menu: {
    xtype: "menu",
    plain: true,
    items: [
      {zoom: -3, text: __("Fit Page"), handler: "menuHandler"},
      {zoom: -1, text: __("Fit Height"), handler: "menuHandler"},
      {zoom: -2, text: __("Fit Width"), handler: "menuHandler"},
      {xtype: "menuseparator"},
      ...Array.from({length: 9}, (_, i) => {
        var zoom = [25, 50, 75, 100, 125, 150, 200, 300, 400][i];
        return {zoom, text: `${zoom}%`, handler: "menuHandler"};
      }),
      {xtype: "menuseparator"},
      {
        xtype: "numberfield",
        itemId: "customZoomField",
        fieldLabel: __("Custom Zoom"),
        labelAlign: "top",
        minValue: 10,
        maxValue: 1000,
        bind: {
          value: "{customField}",
        },
        step: 1,
        listeners: {
          change: function(field, newValue){
            var button = field.up("menu").up("button");
            button.setZoom(newValue || 0);
          },
        },
      },
      {xtype: "menuseparator"},
    ],
  },

  // Private methods
  _calculateWheelDelta: function(event){
    var ratio = window.devicePixelRatio,
      pxFactor;

    switch(true){
      case ratio === 0:
        pxFactor = 1;
        break;
      // case Ext.isLinux && Ext.isChrome:
      //   pxFactor = ratio * 25;
      //   break;
      case Ext.isMac:
        pxFactor = ratio * 3;
        break;
      default:
        pxFactor = ratio * 25;
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
    
    // if(event.deltaX || event.deltaZ) return 0;
    // if(event.wheelDelta) return (event.wheelDeltaY || event.wheelDelta) / 2;
    // if(event.detail){
    //   return Math.abs(event.detail) < 32765 ? 
    //     -event.detail * 20 : 
    //     event.detail / -32765 * 60;
    // }
    return 0;
  },

  _getSvgElement: function(){
    var container = this.up("[appId]").down("#schemeContainer");
    return container.getEl().dom.querySelector("svg");
  },

  // Public methods
  fitSvgToContainer: function(element, zoom){
    var vm = this.getViewModel(),
      size = zoom < 0 ? 100 : zoom || 100,
      container = element.parentNode,
      containerAspectRatio = container.clientWidth / container.clientHeight,
      svgAspectRatio = element.viewBox.baseVal.width / element.viewBox.baseVal.height,
      attributes = {
        height: "100%",
        width: "100%",
        preserveAspectRatio: "xMinYMin meet",
        "object-fit": "contain",
        style: containerAspectRatio > svgAspectRatio ?
          `width: auto; height: ${size}%;` :
          `width: ${size}%; height: auto;`,
      };

    Object.entries(attributes).forEach(([key, value]) => 
      element.setAttribute(key, value),
    );
    if(vm.get("zoom") > 0){
      vm.set("zoom", size);
    }
  },

  getScale: function(){
    var zoom = this.getViewModel().get("zoom");
    return zoom > 0 ? zoom / 100 : 1;
  },
  
  menuHandler: function(item){
    this.getViewModel().set("zoom", item.zoom);
  },

  onWheel: function(event){
    event.preventDefault();
    var scale = this.getScale(),
      delta = this._calculateWheelDelta(event),
      newScale = Math.min(
        Math.max(this.MIN_ZOOM, scale + delta * -this.WHEEL_ZOOM_STEP),
        this.MAX_ZOOM,
      );
    this.getViewModel().set("zoom", Math.round(newScale * 100));
  },

  reset: function(){
    this.getViewModel().set("zoom", this.ZOOM_LEVELS.FIT_PAGE);
    this.setZoom(this.ZOOM_LEVELS.FIT_PAGE);
  },

  restoreZoom: function(){
    var vm = this.getViewModel(),
      zoom = vm.get("zoom"),
      element = this._getSvgElement();
    this.fitSvgToContainer(element, zoom);
  },

  setStyle: function(element, scale){
    var isWidthAuto = element.style.width === "auto",
      isHeightAuto = element.style.height === "auto",
      style = isWidthAuto ? 
        `width: auto; height: ${scale}%` :
        isHeightAuto ?
          `height: auto; width: ${scale}%` :
          null;           
    if(style) element.setAttribute("style", style);
  },
  
  setZoom: function(zoom){
    var element = this._getSvgElement();
    if(!element) return;
    
    if(zoom > 0){
      this.setStyle(element, zoom);
      return;
    }

    switch(zoom){
      case this.ZOOM_LEVELS.FIT_PAGE:
        this.fitSvgToContainer(element, this.ZOOM_LEVELS.FIT_PAGE);
        break;
      case this.ZOOM_LEVELS.FIT_HEIGHT:
        element.setAttribute("style", "height: 100%; width: auto;");
        break;
      case this.ZOOM_LEVELS.FIT_WIDTH:
        element.setAttribute("style", "height: auto; width: 100%;");
        break;
    }
  },
});