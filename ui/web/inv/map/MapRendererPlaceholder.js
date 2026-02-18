//---------------------------------------------------------------------
// Network Map Renderer Placeholder
//---------------------------------------------------------------------
// Copyright (C) 2007-2026 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.MapRendererPlaceholder");

Ext.define("NOC.inv.map.MapRendererPlaceholder", {
  // Link status
  LINK_OK: 0,
  LINK_ADMIN_DOWN: 1,
  LINK_OPER_DOWN: 2,
  LINK_STP_BLOCKED: 3,

  constructor: function(panel){
    console.log("MapRendererPlaceholder.constructor", panel);
    this.panel = panel;
  },

  initFilters: function(){
    console.log("MapRendererPlaceholder.initFilters");
  },

  renderMap: function(data){
    console.log("MapRendererPlaceholder.renderMap", data);
  },

  setLinkStyle: function(link, status){
    console.log("MapRendererPlaceholder.setLinkStyle", link, status);
  },

  applyObjectStatuses: function(data){
    console.log("MapRendererPlaceholder.applyObjectStatuses", data);
  },

  setPaperDimension: function(zoom){
    console.log("MapRendererPlaceholder.setPaperDimension", zoom);
  },

  setZoom: function(zoom){
    console.log("MapRendererPlaceholder.setZoom", zoom);
  },

  setLoadOverlayData: function(data){
    console.log("MapRendererPlaceholder.setLoadOverlayData", data);
  },

  resetOverlayData: function(){
    console.log("MapRendererPlaceholder.resetOverlayData");
  },

  changeLabelText: function(showIPAddress){
    console.log("MapRendererPlaceholder.changeLabelText", showIPAddress);
  },
});