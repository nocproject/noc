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
          flex: 1,
        },
        {
          text: __("Local Name"),
          dataIndex: "local_name",
          flex: 1,
        },
        {
          text: __("Remote Object"),
          dataIndex: "remote_object",
          flex: 1,
        },
        {
          text: __("Remote Name"),
          dataIndex: "remote_name",
          flex: 1,
        },
      ],
      listeners: {
        afterlayout: "afterGridRender",
      },
    },
    {
      xtype: "container",
      flex: 1,
      layout: "fit",
      scrollable: true,
      items: [
        {
          xtype: "image",
          itemId: "scheme",
          hidden: true,
          padding: 5,
        },
      ],
    },
  ],

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
      var imageComponent = me.down("[itemId=scheme]"),
        svg = viz.renderSVGElement(data);
      imageComponent.setHidden(false);
      imageComponent.setSrc(me.svgToBase64(svg.outerHTML));
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
      imageComponent = me.down("#scheme");
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
      bodyHeight = tabPanel.body.getHeight(),
      rowCount = grid.getStore().getCount();
          
    if(rowCount > 0){
      var rowHeight = Ext.fly(grid.getView().getNode(0)).getHeight(),
        gridHeight = (rowCount + 1) * rowHeight + 0.2 * rowHeight;
      if(gridHeight > bodyHeight * 0.5){
        grid.setHeight(bodyHeight * 0.5);
      } else{
        console.log("gridHeight", gridHeight);
        grid.setMaxHeight(gridHeight);
      }
    }
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
});
