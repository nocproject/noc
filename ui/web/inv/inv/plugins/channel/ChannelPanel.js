//---------------------------------------------------------------------
// inv.inv Channel Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.channel.ChannelPanel");

Ext.define("NOC.inv.inv.plugins.channel.ChannelPanel", {
  extend: "Ext.panel.Panel",
  title: __("Channels"),
  closable: false,
  defaultListenerScope: true,
  layout: {
    type: "vbox",
    align: "stretch",
  },
  tbar: [
    {
      xtype: "button",
      glyph: NOC.glyph.refresh,
      tooltip: __("Reload"),
      handler: "onReload",
    },
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
      text: __("Magic"),
      itemId: "adhoc",
      glyph: NOC.glyph.magic,
      handler: "onAddHoc",
    },
  ],
  items: [
    {
      xtype: "grid",
      scrollable: "y",
      columns: [
        {
          xtype: 'glyphactioncolumn',
          width: 50,
          items: [
            {
              glyph: NOC.glyph.star,
              tooltip: __('Mark/Unmark'),
              getColor: function(cls, meta, r){
                return r.get("fav_status") ? NOC.colors.starred : NOC.colors.unstarred;
              },
              handler: "onFavItem",
            },
            {
              glyph: NOC.glyph.edit,
              tooltip: __('Edit'),
              handler: "onEdit",
            },
          ],
        },
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Tech Domain"),
          dataIndex: "tech_domain",
          width: 150,
          renderer: NOC.render.Lookup("tech_domain"),
        },
        {
          text: __("Kind"),
          dataIndex: "kind",
          widht: 50,
        },
        {
          text: __("Topo"),
          dataIndex: "topology",
          width: 120,
        },
        {
          text: __("Discriminator"),
          dataIndex: "discriminator",
          width: 100,
        },
        {
          text: __("From"),
          dataIndex: "from_endpoint",
          flex: 1,
        },
        {
          text: __("To"),
          dataIndex: "to_endpoint",
          flex: 1,
        },
      ],
      listeners: {
        afterlayout: "afterGridRender",
        selectionchange: "onChangeSelection", 
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
  preview: function(data, objectId){
    var me = this,
      grid = me.down("grid"),
      records = data.records || [];
    me.currentId = objectId;
    grid.getStore().loadData(records);
  },
  //
  _render: function(dot){
    var me = this;
    Viz.instance().then(function(viz){ 
      var imageComponent = me.down("[itemId=scheme]"),
        svg = viz.renderSVGElement(dot);
      imageComponent.setHidden(false);
      imageComponent.setSrc(me.svgToBase64(svg.outerHTML));
    });
  },
  //
  renderScheme: function(dot){
    var me = this;
    if(typeof Viz === "undefined"){
      new_load_scripts([
        "/ui/pkg/viz-js/viz-standalone.js",
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
    var base64String = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgString)));
    return base64String;
  },
  //
  onAddHoc: function(){
    var me = this,
      url = "/inv/inv/" + me.currentId + "/plugin/channel/adhoc/"
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: me,
      success: function(response){
        var obj = Ext.decode(response.responseText);
        if(Ext.isEmpty(obj)){
          NOC.info(__("No ad-hoc channels available"));
        } else{
          var adHocWindow = Ext.create("Ext.window.Window", {
            title: __("Create Ad-Hoc channel"),
            height: 400,
            width: 800,
            layout: "fit",
            modal: true,
            items: [
              {
                xtype: "form",
                bodyPadding: 10,
                layout: "anchor",
                defaults: {
                  anchor: "100%",
                  labelWidth: 200,
                },
                items: [
                  {
                    xtype: "grid",
                    scrollable: "y",
                    height: 310,
                    store: new Ext.data.Store({
                      fields: ["controller", "start_endpoint", "start_endpoint__label", "end_endpoint", "end_endpoint__label"],
                      data: obj,
                    }),
                    columns: [
                      {
                        text: __("Start"),
                        dataIndex: "start_endpoint",
                        flex: 1,
                        renderer: NOC.render.Lookup("start_endpoint"),
                      },
                      {
                        text: __("End"),
                        dataIndex: "end_endpoint",
                        flex: 1,
                        renderer: NOC.render.Lookup("end_endpoint"),
                      },
                      {
                        text: __("Controller"),
                        dataIndex: "controller",
                        width: 100,
                      },
                      {
                        text: __("Status"),
                        dataIndex: "status",
                        width: 50,
                        renderer: function(v){
                          return {
                            "new": "<i class='fa fa-plus' style='color:" + NOC.colors.emerald + "' title='New'></i>",
                            "done": "<i class='fa fa-check' style='color:" + NOC.colors.yes + "' title='Done'></i>",
                            "broken": "<i class='fa fa-exclamation-triangle' style='color:" + NOC.colors.no + "' title='Broken'></i>",
                          }[v];
                        },
                      },
                    ],
                    selModel: {
                      selType: "rowmodel",
                      listeners: {
                        selectionchange: function(selModel, selections){
                          if(selections.length > 0){
                            adHocWindow.down("#createButton").setDisabled(false);
                          }
                        },
                        deselect: function(){
                          adHocWindow.down("#createButton").setDisabled(true);
                        },
                      },
                    } },
                ],
                buttons: [
                  {
                    text: __("Create"),
                    itemId: "createButton",
                    glyph: NOC.glyph.plus,
                    disabled: true,
                    handler: function(){
                      var form = this.up("form"),
                        grid = form.down("grid"),
                        selectionModel = grid.getSelectionModel(),
                        selectedRecord = selectionModel.getSelection()[0];
                      Ext.Ajax.request({
                        url: "/inv/inv/" + me.currentId + "/plugin/channel/adhoc/",
                        method: "POST",
                        jsonData: {endpoint: selectedRecord.get("start_endpoint"), controller: selectedRecord.get("controller")},
                        success: function(response){
                          var data = Ext.decode(response.responseText);
                          if(data.status){
                            NOC.info(data.msg);
                            adHocWindow.close();
                            me.onReload(data.channel);
                            NOC.launch("inv.channel", "history", {"args": [data.channel]})
                          } else{
                            NOC.error(data.msg);
                          }
                        },
                        failure: function(response){
                          NOC.error("Failure", response);
                        },
                      });
                    },
                  },
                  {
                    text: __("Cancel"),
                    glyph: NOC.glyph.times,
                    handler: function(){
                      adHocWindow.close();
                    },
                  },
                ],
              },
            ],
          });
          adHocWindow.show();
        }
      },
      failure: function(response){
        NOC.error(__("Failed to get data") + ": " + response.status);
      },
    });
  },
  //
  onChangeSelection: function(grid, selected){
    if(selected.length > 0){
      var me = this,
        recordData = selected[0].getData(),
        url = "/inv/channel/" + recordData.id + "/dot/";
      Ext.Ajax.request({
        url: url,
        method: "GET",
        scope: me,
        success: function(response){
          var obj = Ext.decode(response.responseText);
          this.renderScheme(obj.dot);
        },
        failure: function(response){
          NOC.error(__("Failed to get data") + ": " + response.status);
        },
      });
    }
  },
  //
  afterGridRender: function(grid){
    var me = this,
      gridHeight = grid.getHeight(),
      containerHeight = me.up("tabpanel").body.getHeight();
    if(gridHeight > containerHeight / 2){
      grid.setHeight(containerHeight / 2);
    }
  },
  //
  onReload: function(channelId){
    var me = this,
      grid = me.down("grid");
    Ext.Ajax.request({
      url: `/inv/inv/${me.currentId}/plugin/channel/`,
      method: "GET",
      success: function(response){
        var obj = Ext.decode(response.responseText),
          data = obj.records || [],
          store = grid.getStore(),
          recordIndex = store.findBy(function(record, id){return id === channelId;});
        if(recordIndex !== -1){
          grid.getSelectionModel().select(recordIndex);
        }
        store.loadData(data);

      },
      failure: function(response){
        NOC.error("Error status: " + response.status);
      },
    });
  },
  //
  onFavItem: function(grid, rowIndex){
    var me = this,
      r = grid.getStore().getAt(rowIndex),
      id = r.get("id"),
      action = r.get("fav_status") ? "reset" : "set",
      url = "/inv/channel/favorites/item/" + id + "/" + action + "/";

    Ext.Ajax.request({
      url: url,
      method: "POST",
      scope: me,
      success: function(){
        // Invert current status
        r.set("fav_status", !r.get("fav_status"));
        grid.refresh();
      },
    });
  },
  //
  onEdit: function(grid, rowIndex){
    var r = grid.getStore().getAt(rowIndex),
      id = r.get("id");
    NOC.launch("inv.channel", "history", {"args": [id]})
  },
});
