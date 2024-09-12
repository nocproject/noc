//---------------------------------------------------------------------
// inv.inv SensorPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.crossing.CrossingPanel");

Ext.define("NOC.inv.inv.plugins.crossing.CrossingPanel", {
  extend: "Ext.panel.Panel",
  title: __("Crossing"),
  closable: false,
  layout: {
    type: "vbox",
    align: "stretch",
  },
  defaultListenerScope: true,
  scrollable: false,
  itemId: "crossingPanel",
  tbar: [
    {
      xtype: "combobox",
      store: [
        [0.25, "25%"],
        [0.5, "50%"],
        [0.75, "75%"],
        [1.0, "100%"],
        [1.25, "125%"],
        [1.5, "150%"],
        [2.0, "200%"],
        [3.0, "300%"],
        [4.0, "400%"],
      ],
      width: 100,
      value: 1.0,
      valueField: "zoom",
      editable: false,
      displayField: "label",
      listeners: {
        select: "onZoom",
      },    
    },
    {
      xtype: "button",
      itemId: "detailsButton",
      text: __("Hide details"),
      glyph: NOC.glyph.eye,
      enableToggle: true,
      pressed: true,
      toggleHandler: "showHideDetails",
    },
  ],
  items: [
    {
      xtype: "grid",
      scrollable: "y",
      allowDeselect: true,
      flex: 1,
      split: true,
      columns: [
        {
          dataIndex: "input",
          text: __("Input"),
          width: 150,
        },
        {
          dataIndex: "input_discriminator",
          text: __("Input Discriminator"),
          flex: 1,
        },
        {
          dataIndex: "output",
          text: __("Output"),
          width: 150,
        },
        {
          dataIndex: "output_discriminator",
          text: __("Output Discriminator"),
          flex: 1,
        },
        {
          dataIndex: "gain_db",
          text: __("Gain (dB)"),
          width: 75,
        },
      ],
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
      xtype: "panel",
      flex: 1,
      layout: "auto",
      scrollable: true,
      itemId: "crossingScheme",
    },
  ],
  //
  preview: function(response){
    var me = this;
    me.currentId = response.id;
    me.down("grid").store.loadData(response.data);
    me.renderScheme(response.viz);
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
      var container = me.down("[itemId=crossingScheme]"),
        grid = me.down("grid"),
        svg = viz.renderSVGElement(data);
      
      container.removeAll();
      container.add({
        xtype: "container",
        html: svg.outerHTML,
        listeners: {
          afterrender: function(){
            var svgElement = container.getEl().dom.querySelector("svg"),
              elements = svgElement.querySelectorAll(".selectable");

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
  afterGridRender: function(grid){
    var tabPanel = grid.up("tabpanel"),
      imagePanel = tabPanel.down("#crossingScheme"),
      {grid: gridHeight, image: imageHeight} = this.heightPanels(grid);

    grid.setMaxHeight(gridHeight);
    imagePanel.setHeight(imageHeight);    
  },
  //
  showHideDetails: function(button, pressed){
    var me = this,
      grid = me.down("grid");
    if(pressed){
      button.setText(__("Hide details"));
      button.setGlyph(NOC.glyph.eye);
      grid.show();
    } else{
      button.setText(__("Show details"));
      button.setGlyph(NOC.glyph.eye_slash);
      grid.getSelectionModel().deselectAll();
      grid.hide();
    }
  },
  //
  heightPanels: function(grid){
    var tabPanel = grid.up("tabpanel"),
      bodyHeight = tabPanel.body.getHeight(),
      rowCount = grid.getStore().getCount();

    if(rowCount === 0){
      return {grid: null, image: null};
    }

    var rowHeight = Ext.fly(grid.getView().getNode(0)).getHeight(),
      gridHeight = (rowCount + 1) * rowHeight + 0.2 * rowHeight,
      dockedItemsHeight = grid.up().getDockedItems().reduce(function(totalHeight, item){
        return totalHeight + item.getHeight();
      }, 0),
      halfBodyHeight = bodyHeight * 0.5,
      imageHeight = bodyHeight - halfBodyHeight - dockedItemsHeight,
      detailsButton = tabPanel.down("#detailsButton");

    if(detailsButton.pressed){ 
      return {grid: null, image: bodyHeight - dockedItemsHeight};
    }
    if(gridHeight <= halfBodyHeight){
      return {grid: gridHeight, image: bodyHeight - gridHeight - dockedItemsHeight};
    }

    return {grid: halfBodyHeight, image: imageHeight};
  },
});
