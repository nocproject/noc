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
    this.panel = panel;
  },

  initMap: function(width, height){
    const {nodes, links} = this.generateTopology(20, 20);
    let mainEl = this.panel.down("#topoMap").el,
      miniEl = this.panel.up().down("#miniMap").body,
      topoMap = new map.Topology({
        mainContainer: mainEl.dom,
        minimapContainer: miniEl.dom,
        initialScale: 1,
        minScale: 0.1,
        maxScale: 5,
        gridSize: 20,
        boundsPadding: 12,
        snapThreshold: 5,
        fitToPageOnLoad: true,
        asyncRendering: false,
        enableViewportCulling: true,
        debugLogs: false,
      });
    console.log(width, height);
    console.log("MapRendererPlaceholder.initMap DOM", topoMap);
    topoMap.loadData(nodes, links);
    topoMap.setBoundsPadding(60);
  },

  initFilters: function(){
    console.warn("MapRendererPlaceholder.initFilters");
  },

  renderMap: function(data){
    console.warn("MapRendererPlaceholder.renderMap", data);
  },

  setLinkStyle: function(link, status){
    console.warn("MapRendererPlaceholder.setLinkStyle", link, status);
  },

  applyObjectStatuses: function(data){
    console.warn("MapRendererPlaceholder.applyObjectStatuses", data);
  },

  setPaperDimension: function(zoom){
    console.warn("MapRendererPlaceholder.setPaperDimension", zoom);
  },

  setZoom: function(zoom){
    console.warn("MapRendererPlaceholder.setZoom", zoom);
  },

  setLoadOverlayData: function(data){
    console.warn("MapRendererPlaceholder.setLoadOverlayData", data);
  },

  resetOverlayData: function(){
    console.warn("MapRendererPlaceholder.resetOverlayData");
  },

  changeLabelText: function(showIPAddress){
    console.warn("MapRendererPlaceholder.changeLabelText", showIPAddress);
  },

  generateTopology: function(rows, cols){
    const nodes = [];
    const links = [];
    const spacingX = 220;
    const spacingY = 120;
    const startX = 80;
    const startY = 60;
    let linkSeq = 1;

    for(let row = 0; row < rows; row += 1){
      for(let col = 0; col < cols; col += 1){
        const index = row * cols + col;
        const id = `n${index + 1}`;
        const status = index % 23 === 0 ? "DOWN" : index % 7 === 0 ? "WARN" : "UP";

        nodes.push({
          id,
          x: startX + col * spacingX,
          y: startY + row * spacingY,
          label: `Node ${index + 1}`,
          status,
        });

        if(col < cols - 1){
          links.push({
            id: `l${linkSeq}`,
            sourceId: id,
            targetId: `n${index + 2}`,
            label: "1G",
          });
          linkSeq += 1;
        }

        if(row < rows - 1){
          links.push({
            id: `l${linkSeq}`,
            sourceId: id,
            targetId: `n${index + cols + 1}`,
            label: "10G",
          });
          linkSeq += 1;
        }
      }
    }

    return {nodes, links};
  },
});