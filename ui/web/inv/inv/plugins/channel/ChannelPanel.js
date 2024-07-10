//---------------------------------------------------------------------
// inv.inv Channel Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.channel.ChannelPanel");

Ext.define("NOC.inv.inv.plugins.channel.ChannelPanel", {
  extend: "Ext.panel.Panel",
  title: __("Channel"),
  closable: false,
  defaultListenerScope: true,
  layout: {
    type: "vbox",
    align: "stretch",
  },
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
  ],
  items: [
    {
      xtype: "grid",
      scrollable: "y",
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Tech Domain"),
          dataIndex: "tech_domain",
          width: 100,
          renderer: NOC.render.Lookup("tech_domain"),
        },
      ],
      listeners: {
        afterlayout: function(grid){
          var me = this,
            gridHeight = grid.getHeight(),
            containerHeight = me.up("tabpanel").body.getHeight();
          if(gridHeight > containerHeight / 2){
            grid.setHeight(containerHeight / 2);
          }
        },
        selectionchange: function(grid, selected){
          if(selected.length > 0){
            var recordData = selected[0].getData(),
              url = "/inv/channel/" + recordData.id + "/dot/";
            Ext.Ajax.request({
              url: url,
              method: 'GET',
              scope: this,
              success: function(response){
                var me = this.up(),
                  obj = Ext.decode(response.responseText);
                me.renderScheme(obj.dot);
              },
              failure: function(response){
                NOC.error(__("Failed to get data") + ": " + response.status);
              },
            });
          }
        },
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
  preview: function(data){
    var me = this,
      grid = me.down("grid");
    grid.getStore().loadData(data.records);
  },
  //
  _render: function(dot){
    var me = this,
      viz = new Viz();
    viz.renderSVGElement(dot).then(function(el){
      var imageComponent = me.down("[itemId=scheme]");
      imageComponent.setHidden(false);
      imageComponent.setSrc(me.svgToBase64(el.outerHTML));
    });
  },
  //
  renderScheme: function(dot){
    var me = this;
    if(typeof Viz === "undefined"){
      new_load_scripts([
        'https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js',
        'https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js',          
      ], me, Ext.bind(me._render, me, [dot]));
    } else{
      me._render(dot);
    }
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
    var base64String = "data:image/svg+xml;base64," + btoa(svgString);
    return base64String;
  },
});
