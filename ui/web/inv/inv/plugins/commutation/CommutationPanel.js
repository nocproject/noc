//---------------------------------------------------------------------
// inv.inv Commutation Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.commutation.CommutationPanel");

Ext.define("NOC.inv.inv.plugins.commutation.CommutationPanel", {
  extend: "Ext.panel.Panel",
  title: __("Commutation"),
  closable: false,
  layout: "auto",
  defaultListenerScope: true,
  scrollable: false,
  itemId: "commutationPanel",
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
      flex: 1,
      columns: [
        {
          text: __("Local Object"),
          dataIndex: "local_object",
          renderer: NOC.render.Lookup("local_object"),
          flex: 1,
        },
        {
          text: __("Local Name"),
          dataIndex: "local_name",
          width: 100,
        },
        {
          text: __("Remote Object"),
          dataIndex: "remote_object",
          flex: 1,
          renderer: NOC.render.Lookup("remote_object"),
        },
        {
          text: __("Remote Name"),
          dataIndex: "remote_name",
          width: 100,
        },
      ],
      listeners: {
        afterlayout: "afterGridRender",
        select: function(grid, record){
          document.querySelector("g#" + record.id + " path").style.stroke="#f1c40f";
        },
        deselect: function(grid, record){
          document.querySelector("g#" + record.id + " path").style.stroke="black";
        },
      },
    },
    {
      xtype: "panel",
      flex: 1,
      layout: "auto",
      scrollable: true,
      itemId: "schemePanel",
    },
  ],
  //
  initComponent: function(){
    var me = this;
    me.callParent();
  },
  //
  preview: function(response){
    var me = this,
      grid = me.down("grid"),
      records = response.data || [];
    grid.getStore().loadData(records);
    me.renderScheme(response.viz);
  },
  //
  _render: function(data){
    var me = this;
    Viz.instance().then(function(viz){ 
      var container = me.down("[itemId=schemePanel]"),
        grid = me.down("grid"),
        svg = viz.renderSVGElement(data);
      
      container.removeAll();
      container.add({
        xtype: "container",
        layout: "fit",
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
  onReload: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/commutation/",
      method: "GET",
      scope: me,
      success: function(response){
        me.preview(Ext.decode(response.responseText));
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  //
  onZoom: function(combo){
    var me = this,
      imageComponent = me.down("#schemePanel");
    imageComponent.getEl().dom.style.transformOrigin = "0 0";
    imageComponent.getEl().dom.style.transform = "scale(" + combo.getValue() + ")";
  },
  //
  svgToBase64: function(svgString){
    var base64String = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgString)));
    return base64String;
  },
  //
  afterGridRender: function(grid){
    var tabPanel = grid.up("tabpanel"),
      imagePanel = tabPanel.down("#schemePanel");
    
    var {grid: gridHeight, image: imageHeight} = this.heightPanels(grid);

    grid.setHeight(gridHeight);
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

    if(!detailsButton.pressed){ 
      return {grid: null, image: bodyHeight - dockedItemsHeight};
    }
    if(gridHeight <= halfBodyHeight){
      return {grid: gridHeight, image: bodyHeight - gridHeight - dockedItemsHeight};
    }

    return {grid: halfBodyHeight, image: imageHeight};
  },
});
