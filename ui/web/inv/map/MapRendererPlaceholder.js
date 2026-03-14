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
  // Zoom levels
  FIT_PAGE: -3,
  FIT_HEIGHT: -1,
  FIT_WIDTH: -2,
  removeHandlers: Ext.emptyFn,
  constructor: function(panel){
    this.panel = panel;
  },

  initMap: function(width, height){
    // const {nodes, links} = this.generateTopology(20, 20);
    let mainEl = this.panel.down("#topoMap").el,
      miniEl = this.panel.up().down("#miniMap").body;
    this.topoMap = new map.Topology({
      mainContainer: mainEl.dom,
      minimapContainer: miniEl.dom,
      initialScale: 1,
      minScale: 0.1,
      maxScale: 4,
      gridSize: 20,
      boundsPadding: 64,
      snapThreshold: 5,
      fitToPageOnLoad: true,
      asyncRendering: false,
      enableViewportCulling: true,
      debugLogs: false,
    });
    // this.topoMap.loadData(nodes, links);
    mainEl.dom.addEventListener("topology:cell:highlight", this.onCellSelected.bind(this));
    mainEl.dom.addEventListener("topology:blank:pointerdown", this.onBlankSelected.bind(this));
    mainEl.dom.addEventListener("topology:cell:highlight", this.onCellHighlight.bind(this));
    mainEl.dom.addEventListener("topology:cell:unhighlight", this.onCellUnhighlight.bind(this));
    mainEl.dom.addEventListener("topology:node-search:result", this.onSearchResult.bind(this));
    mainEl.dom.addEventListener("topology:cell:contextmenu", this.onContextMenu.bind(this));
    mainEl.dom.addEventListener("topology:blank:contextmenu", this.onSegmentContextMenu.bind(this));
    mainEl.dom.addEventListener("topology:wheel", this.onWheel.bind(this));

    this.removeHandlers = function(){
      mainEl.dom.removeEventListener("topology:cell:highlight", this.onCellSelected);
      mainEl.dom.removeEventListener("topology:blank:pointerdown", this.onBlankSelected);
      mainEl.dom.removeEventListener("topology:cell:highlight", this.onCellHighlight);
      mainEl.dom.removeEventListener("topology:cell:unhighlight", this.onCellUnhighlight);
      mainEl.dom.removeEventListener("topology:node-search:result", this.onSearchResult);
      mainEl.dom.removeEventListener("topology:cell:contextmenu", this.onContextMenu);
      mainEl.dom.removeEventListener("topology:blank:contextmenu", this.onSegmentContextMenu);
      mainEl.dom.removeEventListener("topology:wheel", this.onWheel);
    };
    console.log(width, height);
    console.log("MapRendererPlaceholder.initMap DOM", this.topoMap);
    this.panel.fireEvent("mapready");
  },

  onCellSelected: function(event){
    const data = event.detail.data;
    console.log("Element attrs", data);
    this.panel.onCellSelected(data);
  },

  onBlankSelected: function(){
    console.log("Blank selected");
    this.panel.onBlankSelected();
  },

  onLinkClick: function(event){
    const attrs = event.detail.attrs;
    console.log("Link attrs", attrs);
  },

  onSegmentContextMenu: function(event){
    console.log("Segment context menu", event);
    this.panel.onSegmentContextMenu(event);
  },

  onContextMenu: function(event){
    console.log("Element context menu", event);
    this.panel.onContextMenu(event);
  },

  onCellHighlight: function(event){
    const data = event.detail.data;
    console.log("Highlight element", data);
    this.panel.onCellHighlight(data);
  },

  onSearchResult: function(event){
    const detail = event.detail;
    if(detail.mode === "labelAndMove"){
      console.log("Search result", detail);
      this.panel.fireEvent("searchResult", detail);
    }
  },
  
  onCellUnhighlight: function(){
    console.log("Unhighlight element");
    this.panel.onCellUnhighlight();
  },

  zoomControlSetCustomField: function(value){
    const zoomControl = this.panel.up("[appId=inv.map]").down("#zoomControl"),
      vm = zoomControl.getViewModel(),
      scale = Math.round(value * 100);
    vm.set("zoom", scale);
  },

  onWheel: function(event){
    this.zoomControlSetCustomField(event.detail.scale);
  },
  
  initFilters: function(){
    console.warn("MapRendererPlaceholder.initFilters");
  },

  renderMap: function(data){
    console.warn("MapRendererPlaceholder.renderMap", data);
    this.topoMap.fromMapData(data);
    this.panel.fireEvent("renderdone");
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
    switch(zoom){
      case this.FIT_PAGE:
        this.topoMap.fitToPage();
        this.zoomControlSetCustomField(this.topoMap.getScale());
        return;
      case this.FIT_HEIGHT:
        this.topoMap.fitToHeight();
        this.zoomControlSetCustomField(this.topoMap.getScale());
        return;
      case this.FIT_WIDTH:
        this.topoMap.fitToWidth();
        this.zoomControlSetCustomField(this.topoMap.getScale());
        return;
    }
       
    this.topoMap.setZoom(zoom/100);
  },

  setLoadOverlayData: function(data){
    console.warn("MapRendererPlaceholder.setLoadOverlayData", data);
  },

  resetOverlayData: function(){
    console.warn("MapRendererPlaceholder.resetOverlayData");
  },

  changeLabelText: function(){
    this.topoMap.toggleNodeLabelMode();
  },

  setEditMode: function(){
    this.topoMap.setMode("edit");
  },
  
  setPanMode: function(){
    this.topoMap.setMode("pan");
  },
  generateTopology: function(rows, cols){
    const nodes = [];
    const links = [];
    const spacingX = 220;
    const spacingY = 120;
    const startX = 80;
    const startY = 60;
    let linkSeq = 1;
    const statusClasses = ["gf-ok", "gf-warn", "gf-unknown", "gf-fail"];

    const lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.";

    for(let row = 0; row < rows; row += 1){
      for(let col = 0; col < cols; col += 1){
        const index = row * cols + col;
        const id = `n${index + 1}`;
        const statusClass = statusClasses[Math.floor(Math.random() * statusClasses.length)];
      
        const textLen = Math.floor(Math.random() * 30);
        const loremText = lorem.slice(0, textLen);

        nodes.push({
          id,
          x: startX + col * spacingX,
          y: startY + row * spacingY,
          attrs: {
            title: {
              text: `Node ${index + 1} ${loremText}`,
            },
            ipaddr: {
              text: `10.42.${row + 1}.${col + 1}`,
            },
            icon: {
              status: statusClass,
            },
          },
        });

        if(col < cols - 1){
          links.push({
            id: `l${linkSeq}`,
            sourceId: id,
            targetId: `n${index + 2}`,
            // label: "1G",
          });
          linkSeq += 1;
        }

        if(row < rows - 1){
          links.push({
            id: `l${linkSeq}`,
            sourceId: id,
            targetId: `n${index + cols + 1}`,
            // label: "10G",
          });
          linkSeq += 1;
        }
      }
    }

    return {nodes, links};
  },
});