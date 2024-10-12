//---------------------------------------------------------------------
// inv.inv Abstract Plugin for view SVG scheme from viz-js
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.SchemePluginAbstract");

Ext.define("NOC.inv.inv.plugins.SchemePluginAbstract", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.Zoom",
  ],
  mixins: [
    "NOC.inv.inv.plugins.Mixins",
  ],
  closable: false,
  layout: {
    type: "vbox",
    align: "stretch",
  },
  defaultListenerScope: true,
  scrollable: false,
  viewModel: {
    data: {
      currentId: null,
      showDetails: true,
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
      xtype: "button",
      itemId: "downloadSvgButton",
      tooltip: __("Download image as SVG"),
      glyph: NOC.glyph.download,
      handler: "onDownloadSVG",
    },
  ],
  items: [
    {
      xtype: "grid",
      scrollable: "y",
      flex: 1,
      bind: {
        hidden: "{!showDetails}",
      },
      emptyText: __("No data"),
      allowDeselect: true,
      split: true,
      store: {
        data: [],
      },
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
      layout: "auto",
      scrollable: true,
      listeners: {
        afterlayout: "afterPanelsRender",
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
      grid = me.down("grid"),
      records = response.data || response.records || [];
    me.currentId = objectId;
    grid.getStore().loadData(records);
    if(Object.prototype.hasOwnProperty.call(response, "viz")){
      me.renderScheme(response.viz);
    }
  },
  //
  renderScheme: function(data){
    var me = this;
    if(typeof Viz === "undefined"){
      new_load_scripts([
        "/ui/pkg/viz-js/viz-standalone.js",
      ], me, Ext.bind(me._render, me, [data]));
    } else{
      me._render(data);
    }
  },
  //
  _render: function(data){
    var me = this;
    Viz.instance().then(function(viz){ 
      var container = me.down("[itemId=schemeContainer]"),
        grid = me.down("grid"),
        svg = viz.renderSVGElement(data);
           
      container.removeAll();
      container.add({
        xtype: "container",
        itemId: "scheme",
        filenamePrefix: me.itemId.replace("Panel", ""),
        layout: "fit",
        html: svg.outerHTML,
        listeners: {
          afterrender: function(){
            var svgElement = container.getEl().dom.querySelector("svg"),
              elements = svgElement.querySelectorAll(".selectable"),
              zoomControl = me.down("#zoomControl");

            zoomControl.fitSvgToContainer();
            elements.forEach(function(element){
              element.addEventListener("click", function(){
                var record = grid.getStore().getById(element.id);
                
                if(record){
                  grid.getSelectionModel().select(record);
                }
              });
            });
          },
        },
      });
    });
  },
  //
  onReload: function(){
    var me = this;
    me.mask(__("Loading..."));
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/" + this.itemId.replace("Panel", "") + "/",
      method: "GET",
      scope: me,
      success: function(response){
        me.unmask();
        me.preview(Ext.decode(response.responseText), me.currentId);
      },
      failure: function(){
        me.unmask();
        NOC.error(__("Failed to get data"));
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
    console.log('heightPanels called');
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
});