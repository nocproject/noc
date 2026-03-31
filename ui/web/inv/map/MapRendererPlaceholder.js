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

  getMapModule: function(){
    var module = window.map;
    if(!module || !module.Topology){
      NOC.error(__("Map module is not loaded"));
      return null;
    }
    return module;
  },

  initMap: function(){
    let mainEl = this.panel.down("#topoMap").el,
      miniEl = this.panel.up().down("#miniMap").body,
      module = this.getMapModule();
    if(!module){
      return;
    }

    this.topoMap = new module.Topology({
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
    let boundHandlers = {
      onCellSelected: this.onCellSelected.bind(this),
      onCellUnhighlight: this.onCellUnhighlight.bind(this),
      onContextMenu: this.onContextMenu.bind(this),
      onElementDblClick: this.onElementDblClick.bind(this),
      onBlankSelected: this.onBlankSelected.bind(this),
      onSegmentContextMenu: this.onSegmentContextMenu.bind(this),
      onSearchResult: this.onSearchResult.bind(this),
      onScaleChange: this.onScaleChange.bind(this),
    };
    mainEl.dom.addEventListener(module.CELL_HIGHLIGHT_EVENT, boundHandlers.onCellSelected);
    mainEl.dom.addEventListener(module.CELL_UNHIGHLIGHT_EVENT, boundHandlers.onCellUnhighlight);
    mainEl.dom.addEventListener(module.CELL_CONTEXTMENU_EVENT, boundHandlers.onContextMenu);
    mainEl.dom.addEventListener(module.ELEMENT_POINTERDBLCLICK_EVENT, boundHandlers.onElementDblClick);
    mainEl.dom.addEventListener(module.BLANK_POINTERDOWN_EVENT, boundHandlers.onBlankSelected);
    mainEl.dom.addEventListener(module.BLANK_CONTEXTMENU_EVENT, boundHandlers.onSegmentContextMenu);
    mainEl.dom.addEventListener(module.NODE_SEARCH_RESULT_EVENT, boundHandlers.onSearchResult);
    mainEl.dom.addEventListener(module.SCALE_CHANGE_EVENT, boundHandlers.onScaleChange);

    this.removeHandlers = function(){
      mainEl.dom.removeEventListener(module.CELL_HIGHLIGHT_EVENT, boundHandlers.onCellSelected);
      mainEl.dom.removeEventListener(module.CELL_UNHIGHLIGHT_EVENT, boundHandlers.onCellUnhighlight);
      mainEl.dom.removeEventListener(module.CELL_CONTEXTMENU_EVENT, boundHandlers.onContextMenu);
      mainEl.dom.removeEventListener(module.ELEMENT_POINTERDBLCLICK_EVENT, boundHandlers.onElementDblClick);
      mainEl.dom.removeEventListener(module.BLANK_POINTERDOWN_EVENT, boundHandlers.onBlankSelected);
      mainEl.dom.removeEventListener(module.BLANK_CONTEXTMENU_EVENT, boundHandlers.onSegmentContextMenu);
      mainEl.dom.removeEventListener(module.NODE_SEARCH_RESULT_EVENT, boundHandlers.onSearchResult);
      mainEl.dom.removeEventListener(module.SCALE_CHANGE_EVENT, boundHandlers.onScaleChange);
      boundHandlers = null;
    };
    this.panel.fireEvent("mapready");
  },

  onCellSelected: function(event){
    const data = event.detail.data;
    this.panel.onCellSelected(data);
  },

  onBlankSelected: function(){
    this.panel.onBlankSelected();
  },

  onSegmentContextMenu: function(event){
    this.panel.onSegmentContextMenu(event);
  },

  onContextMenu: function(event){
    this.panel.onContextMenu(event);
  },

  onElementDblClick: function(event){
    const data = event.detail.data;
    this.panel.onElementDoubleClick(data);
  },

  onSearchResult: function(event){
    const detail = event.detail;
    if(detail.mode === "labelAndMove"){
      this.panel.fireEvent("searchResult", detail);
    }
  },

  onCellUnhighlight: function(){
    this.panel.onCellUnhighlight();
  },

  zoomControlSetCustomField: function(value){
    const zoomControl = this.panel.up("[appId=inv.map]").down("#zoomControl"),
      vm = zoomControl.getViewModel(),
      scale = Math.round(value * 100);
    vm.set("zoom", scale);
  },

  onScaleChange: function(event){
    this.zoomControlSetCustomField(event.detail.scale);
  },

  renderMap: function(data){
    this.topoMap.convertAndLoad(data);
    this.panel.app.viewStpButton.setDisabled(!data.caps.includes("Network | STP"));
    // Run status polling
    this.panel.startPolling();
    this.panel.fireEvent("renderdone");
  },

  setLinkStyle: function(link, status){
    console.warn("MapRendererPlaceholder.setLinkStyle", link, status);
  },

  applyObjectStatuses: function(data){
    this.topoMap.data.elements.setStatuses(data);
    // this.topoMap.data.elements.setRandomStatuses([
    //   {status_code: 0, metrics_label: ""},
    //   {status_code: 1, metrics_label: "CPU<br/>12%"},
    //   {status_code: 2, metrics_label: "CPU<br/>78%"},
    //   {status_code: 4, metrics_label: "Link<br/>Down"},
    // ]);
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
});