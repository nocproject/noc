//---------------------------------------------------------------------
// inv.inv Abstract Plugin for view SVG scheme from viz-js
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.VizSchemePluginAbstract");

Ext.define("NOC.inv.inv.plugins.VizSchemePluginAbstract", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.Zoom",
    "NOC.inv.inv.plugins.DownloadButton",
  ],
  mixins: [
    "NOC.core.mixins.Export",
  ],
  xtype: "vizscheme",
  closable: false,
  layout: {
    type: "vbox",
    align: "stretch",
  },
  defaultListenerScope: true,
  scrollable: false,
  viewModel: {
    stores: {
      gridStore: {
        data: [],
        listeners: {
          datachanged: "onDataChanged",
        },
      },
    },
    data: {
      currentId: null,
      showDetails: true,
      zoomDisabled: true,
      downloadSvgItemDisabled: true,
      downloadCsvItemDisabled: true,
      totalCount: 0,
    },
    formulas: {
      detailsButtonText: function(get){
        return get("showDetails") ? __("Hide details") : __("Show details");
      },
      detailsButtonGlyph: function(get){
        return get("showDetails") ? "xf06e@FontAwesome" : "xf070@FontAwesome";
      },
    },
  },
  tbar: [
    {
      itemId: "reloadButton",
      glyph: NOC.glyph.refresh,
      tooltip: __("Reload"),
      handler: "onReload",
    },
    {
      xtype: "invPluginsZoom",
      itemId: "zoomControl",
      bind: {
        disabled: "{zoomDisabled}",
      },
    },
    {
      xtype: "button",
      itemId: "detailsButton",
      reference: "detailsButton",
      enableToggle: true,
      bind: {
        text: "{detailsButtonText}",
        glyph: "{detailsButtonGlyph}",
        pressed: "{showDetails}",
      },
      toggleHandler: "showHideDetails",
    },
    {
      xtype: "invPluginsDownloadButton",
      itemId: "downloadButton",
    },
    "->",
    {
      xtype: "tbtext",
      bind: {
        html: __("Total") + ": {totalCount}",
      },
    },
  ],
  items: [
    {
      xtype: "grid",
      scrollable: "y",
      flex: 1,
      bind: {
        hidden: "{!showDetails}",
        store: "{gridStore}",
      },
      emptyText: __("No data"),
      allowDeselect: true,
      split: true,
      columns: [],
      listeners: {
        afterlayout: "afterGridRender",
        select: function(grid, record){
          var element = document.querySelector("g#" + record.id + " path");
          if(element){
            element.style.stroke="#f1c40f";
          }
        },
        deselect: function(grid, record){
          var element = document.querySelector("g#" + record.id + " path");
          if(element){
            element.style.stroke="black";
          }
        },
      },
    },
    {
      xtype: "splitter",
    },
    {
      xtype: "container",
      itemId: "schemeContainer",
      flex: 1,
      layout: "fit",
      scrollable: true,
      listeners: {
        afterlayout: "afterPanelsRender",
        click: {
          element: "el",
          fn: "onSchemeClick",
        },
      },
    },
  ],
  listeners: {
    added: function(){
      var grid = this.down("gridpanel");
      if(grid && this.gridColumns){
        grid.reconfigure(null, this.gridColumns);
      }
    },
  },
  //
  preview: function(response, objectId){
    var me = this,
      vm = me.getViewModel(),
      records = response.data || response.records || [];
    vm.set("currentId", objectId);
    vm.getStore("gridStore").removeAll();
    vm.getStore("gridStore").loadData(records);
    if(Object.prototype.hasOwnProperty.call(response, "viz")){
      me.renderScheme(response.viz);
    }
  },
  //
  renderScheme: function(data){
    var me = this;
    if(typeof Viz === "undefined"){
      Ext.Loader.loadScript({
        url: "/ui/pkg/viz-js/viz-standalone.js",
        onLoad: function(){
          this._render(data);
        },
        scope: me,
      });
    } else{
      me._render(data);
    }
  },
  //
  _render: function(data){
    var me = this;
    Viz.instance().then(function(viz){ 
      var container = me.down("[itemId=schemeContainer]"),
        svg = viz.renderSVGElement(data);
      svg.setAttribute("height", "100%");
      svg.setAttribute("width", "100%");
      svg.setAttribute("preserveAspectRatio", "xMinYMin meet");
      svg.setAttribute("object-fit", "contain");
      container.setHtml(svg.outerHTML);
      me.down("#zoomControl").reset();
      me.getViewModel().set("zoomDisabled", false);
      me.getViewModel().set("downloadSvgItemDisabled", false);
    });
  },
  //
  onReload: function(){
    var me = this,
      currentId = me.getViewModel().get("currentId");
    me.getData(function(response){
      me.preview(Ext.decode(response.responseText), currentId);
      me.down("#zoomControl").reset();
    });
  },
  //
  getData: function(cb){
    var me = this,
      pluginName = me.itemId.replace("Panel", ""),
      currentId = me.getViewModel().get("currentId"),
      maskComponent = me.up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show("fetching", [pluginName]);
    Ext.Ajax.request({
      url: "/inv/inv/" + currentId + "/plugin/" + pluginName + "/",
      method: "GET",
      scope: me,
      success: cb,
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
      callback: function(){
        maskComponent.hide(messageId);
      },
    });
  },
  //
  afterPanelsRender: function(imagePanel){
    var grid = imagePanel.previousSibling("grid"),
      {grid: gridHeight, image: imageHeight} = this.heightPanels(grid);

    grid.setHeight(gridHeight);
    imagePanel.setHeight(imageHeight);    
  },
  //
  afterGridRender: function(grid){
    var tabPanel = grid.up("tabpanel"),
      imagePanel = tabPanel.down("#schemeContainer"),
      {grid: gridHeight, image: imageHeight} = this.heightPanels(grid);

    grid.setMaxHeight(gridHeight);
    imagePanel.setHeight(imageHeight);    
  },
  //
  heightPanels: function(grid){
    var tabPanel = grid.up("tabpanel"),
      vm = this.getViewModel(),
      isShowDetails = vm.get("showDetails"),
      bodyHeight = tabPanel.body.getHeight(),
      rowCount = grid.getStore().getCount();

    if(!isShowDetails || !grid.getView().getNode(0)){
      return {grid: null, image: bodyHeight};
    }

    var rowHeight = Ext.fly(grid.getView().getNode(0)).getHeight(),
      gridHeight = (rowCount + 1) * rowHeight + 0.2 * rowHeight,
      dockedItemsHeight = this.getDockedItems().reduce(function(totalHeight, item){
        return totalHeight + item.getHeight();
      }, 0),
      halfBodyHeight = bodyHeight * 0.5,
      imageHeight = bodyHeight - halfBodyHeight - dockedItemsHeight;

    if(gridHeight <= halfBodyHeight){
      return {grid: gridHeight, image: bodyHeight - gridHeight - dockedItemsHeight};
    }
    return {grid: halfBodyHeight, image: imageHeight};
  },
  //
  showHideDetails: function(button, pressed){
    var me = this,
      grid = me.down("grid");
    if(!pressed){
      grid.getSelectionModel().deselectAll();
    }
  },
  onDataChanged: function(store){
    var vm = this.getViewModel();
    if(vm){
      vm.set("totalCount", store.getCount());
    }
  },
  //
  onSchemeClick: function(event, target){
    if(target.parentNode && target.parentNode.classList.contains("selectable")){
      var grid = this.down("grid");
      if(grid){
        var record = grid.getStore().getById(target.parentNode.id);
        if(record) grid.getSelectionModel().select(record);
      }
    }
  },
});