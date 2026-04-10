//---------------------------------------------------------------------
// Network Map Renderer Placeholder
//---------------------------------------------------------------------
// Copyright (C) 2007-2026 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.MapRendererPlaceholder");

Ext.define("NOC.inv.map.MapRendererPlaceholder", {
  LOAD_METRICS: ["Interface | Load | In", "Interface | Load | Out"],
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
  currentStpBlocked: {},

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
    let document = this.topoMap.convertMapData(data);
    this.topoMap.loadDocument(document);
    this.panel.app.viewStpButton.setDisabled(!data.caps.includes("Network | STP"));
    // Run status polling
    this.panel.startPolling();
    this.panel.fireEvent("renderdone");
  },

  setLinkStyle: function(linkId, status){
    console.warn("MapRendererPlaceholder.setLinkStyle", linkId, status);
    this.topoMap.setLinkStatus(linkId, status);
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

  // Display links load
  // data is dict of
  // metric ->
  // "4": {
  //        "admin_status": true,
  //        "oper_status": true,
  //        "Interface | Load | In": 403,
  //        "Interface | Load | Out": 2841
  // },
  setLoadOverlayData: function(data){
    let links = this.topoMap.data.links.getAll();
    if(! links){
      return;
    }
    for(let link of links){
      const ports = link.data.ports,
        isDown = (key) => !(data[ports[0]]?.[key] ?? true) || !(data[ports[1]]?.[key] ?? true);
      //
      if(isDown("admin_status")){
        this.setLinkStyle(link.id, this.LINK_ADMIN_DOWN);
      } else if(isDown("oper_status")){
        this.setLinkStyle(link.id, this.LINK_OPER_DOWN);
      } else if(!this.currentStpBlocked[link.id]){
        this.applyLinkLoad(link, data);
      }
    }
  },

  applyLinkLoad: function(link, data){
    let bw, td, dt, lu, 
      ports = link.data.ports,
      // Get bandwidth
      sIn = data[ports[0]]?.[this.LOAD_METRICS[0]] ?? 0.0,
      sOut = data[ports[0]]?.[this.LOAD_METRICS[1]] ?? 0.0,
      dIn = data[ports[1]]?.[this.LOAD_METRICS[0]] ?? 0.0,
      dOut = data[ports[1]]?.[this.LOAD_METRICS[1]] ?? 0.0;

    bw = this.topoMap.data.links.getLinkBw(link.id);
    // Destination to target
    td = Math.max(sOut, dIn);
    // Target to destination
    dt = Math.max(sIn, dOut);
    if(bw){
      // Link utilization
      lu = 0.0;
      if(bw.in && bw.in > 0){
        lu = Math.max(lu, dt / bw.in);
      }
      if(bw.out && bw.out > 0){
        lu = Math.max(lu, td / bw.out);
      }
      this.topoMap.setLinkUtilization(link.id, lu);
    }
    // save link utilization
    link.data.metrics = ports.map((port) => ({
      port: port,
      metrics: this.LOAD_METRICS.map((metric) => ({
        metric: metric,
        value: data?.[port]?.[metric] ?? "-",
      })),
    }));
  },

  resetOverlayData: function(){
    this.topoMap.resetAllLinkPresentation();
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

  getMetrics: function(metrics){
    let interfaces = this.topoMap.getInterfaces();
    return metrics.flatMap((m) => interfaces.map((i) => ({...i, metric: m})));
  },
});