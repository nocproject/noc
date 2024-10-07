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
  layout: "card",
  requires: [
    "NOC.inv.inv.plugins.channel.MagicPanel",
  ],
  tbar: [
    {
      text: __("Close"),
      itemId: "closeInvChannelBtn",
      glyph: NOC.glyph.arrow_left,
      hidden: true,
      handler: "showChannelPanel",
    },
    {
      xtype: "button",
      glyph: NOC.glyph.refresh,
      tooltip: __("Reload"),
      handler: "onReload",
    },
    {
      xtype: "combobox",
      itemId: "zoomInvChannelCombo",
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
      editable: false,
      listeners: {
        select: "onZoom",
      },
    },
    {
      xtype: "button",
      text: __("Magic"),
      itemId: "adhocInvChannelBtn",
      glyph: NOC.glyph.magic,
      handler: "onAddHoc",
    },
    {
      text: __("Create"),
      itemId: "createInvChannelBtn",
      glyph: NOC.glyph.plus,
      disabled: true,
      hidden: true,
      handler: "onCreateAdHoc",
    },
    {
      xtype: "button",
      itemId: "downloadSvgChannelBtn",
      tooltip: __("Download image as SVG"),
      glyph: NOC.glyph.download,
      disabled: true,
      handler: "onDownloadSVG",
    },
  ],
  items: [
    {
      xtype: "panel",
      layout: {
        type: "vbox",
        align: "stretch",
      },
      items: [
        {
          xtype: "grid",
          scrollable: "y",
          split: true,
          store: {
            data: [],
          },
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
              width: 50,
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
          xtype: "splitter",
        },
        {
          xtype: "container",
          flex: 1,
          itemId: "schemeContainer",
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
    },
    {
      xtype: "invchannelmagic",
      listeners: {
        magicselectionchange: "onMagicSelectionChange",
      },
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
  _render: function(data){
    var me = this;
    Viz.instance().then(function(viz){ 
      var imageComponent = me.down("#scheme"),
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
      url = "/inv/inv/" + me.currentId + "/plugin/channel/adhoc/";
    me.mask(__("Loading..."));
    me.down("#createInvChannelBtn").setDisabled(true);
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: me,
      success: function(response){
        var obj = Ext.decode(response.responseText);
        if(Ext.isEmpty(obj)){
          NOC.info(__("No ad-hoc channels available"));
        } else{
          me.showMagicPanel();
          me.down("[xtype=invchannelmagic] grid").getStore().loadData(obj);
          me.unmask();
        }
      },
      failure: function(response){
        NOC.error(__("Failed to get data") + ": " + response.status);
        me.unmask();
      },
    });
  },
  //
  onChangeSelection: function(grid, selected){
    var me = this,
      downloadBtn = me.down("#downloadSvgChannelBtn");
    if(selected.length > 0){
      var recordData = selected[0].getData(),
        schemeContainer = me.down("#schemeContainer"),
        url = "/inv/channel/" + recordData.id + "/viz/";
      downloadBtn.setDisabled(false);
      schemeContainer.mask(__("Loading..."));
      Ext.Ajax.request({
        url: url,
        method: "GET",
        scope: me,
        success: function(response){
          var obj = Ext.decode(response.responseText);
          this.renderScheme(obj.data);
          schemeContainer.unmask();
        },
        failure: function(response){
          NOC.error(__("Failed to get data") + ": " + response.status);
          schemeContainer.unmask();
        },
      });
    } else{
      downloadBtn.setDisabled(true);
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
  onReload: function(){
    var me = this,
      activeItem = me.getLayout().getActiveItem();
    
    if(activeItem.xtype === "panel"){
      me.reloadChannelGrid(activeItem);
    }

    if(activeItem.xtype === "invchannelmagic"){
      me.onAddHoc();
    }
    //   grid = me.down("grid");
    // Ext.Ajax.request({
    //   url: `/inv/inv/${me.currentId}/plugin/channel/`,
    //   method: "GET",
    //   success: function(response){
    //     var obj = Ext.decode(response.responseText),
    //       data = obj.records || [],
    //       store = grid.getStore(),
    //       recordIndex = store.findBy(function(record, id){return id === channelId;});
    //     if(recordIndex !== -1){
    //       grid.getSelectionModel().select(recordIndex);
    //     }
    //     store.loadData(data);
    //     if(selectRow){
    //       var selIndex = store.find("id", channelId);
    //       if(selIndex !== -1){
    //         grid.getSelectionModel().select(selIndex);
    //       }
    //     }
    //   },
    //   failure: function(response){
    //     NOC.error("Error status: " + response.status);
    //   },
    // });
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
  //
  onDownloadSVG: function(){
    var me = this,
      imageComponent = me.down("#scheme"),
      svgBase64 = imageComponent.getEl().dom.src.replace("data:image/svg+xml;base64,", ""),
      svg = atob(svgBase64),
      svgBlob = new Blob([svg], {type: "image/svg+xml"}),
      svgUrl = URL.createObjectURL(svgBlob),
      a = document.createElement("a");
    a.href = svgUrl;
    a.download = "channel-scheme-" + me.currentId + ".svg";
    a.click();
  },
  //
  showChannelPanel: function(){
    this.down("#adhocInvChannelBtn").show();
    this.down("#zoomInvChannelCombo").show();
    this.down("#downloadSvgChannelBtn").show();
    this.down("#closeInvChannelBtn").hide();
    this.down("#createInvChannelBtn").hide(); 
    this.getLayout().setActiveItem(0);
  },
  //
  showMagicPanel: function(){
    this.getLayout().setActiveItem(1);
    this.down("#adhocInvChannelBtn").hide();
    this.down("#zoomInvChannelCombo").hide();
    this.down("#downloadSvgChannelBtn").hide();
    this.down("#createInvChannelBtn").show();
    this.down("#closeInvChannelBtn").show();
  },
  //
  reloadChannelGrid: function(panel){
    var me = this,
      grid = panel.down("grid");
    panel.mask(__("Loading..."));
    Ext.Ajax.request({
      url: `/inv/inv/${me.currentId}/plugin/channel/`,
      method: "GET",
      success: function(response){
        var obj = Ext.decode(response.responseText),
          data = obj.records || [],
          store = grid.getStore();
        store.loadData(data);
        panel.unmask();
      },
      failure: function(response){
        panel.unmask();
        NOC.error("Error status: " + response.status);
      },
    });
  },
  //
  onMagicSelectionChange: function(disable){
    this.down("#createInvChannelBtn").setDisabled(disable);
  },
  //
  onCreateAdHoc: function(){
    var me = this,
      grid = me.down("invchannelmagic").down("grid"),
      selectionModel = grid.getSelectionModel(),
      selectedRecord = selectionModel.getSelection()[0];

    me.mask(__("Loading..."));
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/channel/adhoc/",
      method: "POST",
      jsonData: {endpoint: selectedRecord.get("start_endpoint"), controller: selectedRecord.get("controller")},
      success: function(response){
        var data = Ext.decode(response.responseText);
        if(data.status){
          NOC.info(data.msg);
          NOC.launch("inv.channel", "history", {"args": [data.channel]})
        } else{
          NOC.error(data.msg);
        }
        me.unmask();
      },
      failure: function(response){
        me.unmask();
        NOC.error("Failure", response);
      },
    });
  },
});
