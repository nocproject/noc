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
  layout: {
    type: 'vbox',
    align: 'stretch',
  },
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
      itemId: "scheme",
      flex: 1,
      padding: 5,
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
      me.down("[itemId=scheme]").update(el.outerHTML);
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
});
