//---------------------------------------------------------------------
// inv.inv Abstract Plugin for view SVG scheme from backend 
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.FileSchemePluginAbstract");

Ext.define("NOC.inv.inv.plugins.FileSchemePluginAbstract", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.SideButton",
    "NOC.inv.inv.plugins.Zoom",
    "NOC.inv.inv.plugins.FileSchemeController",
  ],
  xtype: "filescheme",
  app: null,
  scrollable: true,
  closable: false,
  controller: "filescheme",
  layout: {
    type: "vbox",
    align: "stretch",
  },
  viewModel: {
    data: {
      currentId: null,
      side: "front",
      hasRear: false,
      edit: false,
    },
    formulas: {
      isFrontPressed: function(get){
        return get("side") === "front";
      },
      isRearPressed: function(get){
        return get("side") === "rear";
      },
    },
  },
  items: [
    {
      xtype: "container",
      itemId: "schemeContainer",
      flex: 1,
      layout: "fit",
      scrollable: true,
      listeners: {
        click: {
          element: "el",
          fn: "onSchemeClick",
        },
      },
    },
  ],
  tbar: [
    {
      glyph: NOC.glyph.refresh,
      tooltip: __("Reload"),
      handler: "onReload",
    },
    "-",
    {
      xtype: "invPluginsSegmented",
      listeners: {
        sideChange: "onSideChange",
      },
    },
    "-",
    {
      xtype: "invPluginsZoom",
      itemId: "zoomControl",
    },
    {
      xtype: "button",
      tooltip: __("Download image as SVG"),
      glyph: NOC.glyph.download,
      handler: "onDownloadSVG",
    },
  ],
  preview: function(data){
    var me = this,
      // padding = 0,
      viewPanel = me.down("#schemeContainer"),
      vm = me.getViewModel(),
      name = me.itemId.replace("Panel", "").toLowerCase(),
      side = vm.get("side"),
      svgUrl = me.svgUrlTemplate ? me.svgUrlTemplate.apply({id: data.id, name: name, side: side})
      : data.views[side === "front" ? 0 : 1].src,
      maskComponent = me.up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show("fetching", [name]);
    vm.set("currentId", data.id);
    //
    viewPanel.filenamePrefix = `${name}-${side}`;
    Ext.Ajax.request({
      url: svgUrl,
      method: "GET",
      success: function(response){
        var svg,
          parser = new DOMParser(),
          zoom = function(event){
            event.preventDefault();
            scale += event.deltaY * -0.01;
            scale = Math.min(Math.max(0.125, scale), 6);
            zoomControl.setZoomByValue(scale);
          },
          parserResult = parser.parseFromString(response.responseText, "image/svg+xml"),
          parserError = parserResult.querySelector("parsererror"),
          zoomControl = viewPanel.up().down("#zoomControl"), 
          scale = zoomControl.getZoom();
        
        if(parserError){
          NOC.error("Failed to parse SVG: " + parserError.textContent);
          return;
        }
        viewPanel.setHtml(parserResult.documentElement.outerHTML);
        svg = viewPanel.getEl().dom.querySelector("svg");
        svg.onwheel = zoom;
        zoomControl.restoreZoom();
      },
      failure: function(response){
        NOC.error("Failed to load SVG: " + response.status);
      },
      callback: function(){
        maskComponent.hide(messageId);
      },
    });
    // ToDo refactoring backend to rack like facade plugin
    if(Object.prototype.hasOwnProperty.call(data, "load")){ // Rack plugin
      vm.get("gridStore").loadData(data.load);
    }
    if(Object.prototype.hasOwnProperty.call(data, "views")){ // Facade plugin
      vm.set("hasRear", data.views.length > 1);
    } else{
      vm.set("hasRear", true);
    }
  },
});