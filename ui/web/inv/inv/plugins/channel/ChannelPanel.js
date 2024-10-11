//---------------------------------------------------------------------
// inv.inv Channel Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.channel.ChannelPanel");

Ext.define("NOC.inv.inv.plugins.channel.ChannelPanel", {
  extend: "NOC.inv.inv.plugins.SchemePluginAbstract",
  title: __("Channels"),
  itemId: "channelPanel",
  layout: "card",
  requires: [
    "NOC.inv.inv.plugins.channel.MagicPanel",
  ],
  // tbar: [
  //   {
  //     text: __("Close"),
  //     itemId: "closeInvChannelBtn",
  //     glyph: NOC.glyph.arrow_left,
  //     hidden: true,
  //     handler: "showChannelPanel",
  //   },
  //   {
  //     xtype: "button",
  //     glyph: NOC.glyph.refresh,
  //     tooltip: __("Reload"),
  //     handler: "onReload",
  //   },
  //   {
  //     xtype: "invPluginsZoom",
  //     itemId: "zoomControl",
  //     appPanel: "channelPanel",
  //   },
  //   {
  //     xtype: "button",
  //     text: __("Magic"),
  //     itemId: "adhocInvChannelBtn",
  //     glyph: NOC.glyph.magic,
  //     handler: "onAddHoc",
  //   },
  //   {
  //     text: __("Create"),
  //     itemId: "createInvChannelBtn",
  //     glyph: NOC.glyph.plus,
  //     disabled: true,
  //     hidden: true,
  //     handler: "onCreateAdHoc",
  //   },
  //   {
  //     xtype: "button",
  //     itemId: "downloadSvgChannelBtn",
  //     tooltip: __("Download image as SVG"),
  //     glyph: NOC.glyph.download,
  //     disabled: true,
  //     handler: "onDownloadSVG",
  //   },
  // ],
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
          allowDeselect: true,
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
            deselect: "onDeselect",
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
    },
    {
      xtype: "invchannelmagic",
      listeners: {
        magicselectionchange: "onMagicSelectionChange",
      },
    },
  ],
  initComponent: function(){
    var parentItems = Ext.Array.clone(this.items),
      tbarItems = Ext.Array.clone(this.tbar),
      closeBtn = {
        text: __("Close"),
        itemId: "closeInvChannelBtn",
        glyph: NOC.glyph.arrow_left,
        hidden: true,
        handler: "showChannelPanel",
      },
      magicBtn = {
        text: __("Magic"),
        itemId: "adhocInvChannelBtn",
        glyph: NOC.glyph.magic,
        handler: "onAddHoc",
      },
      createBtn = {
        text: __("Create"),
        itemId: "createInvChannelBtn",
        glyph: NOC.glyph.plus,
        disabled: true,
        hidden: true,
        handler: "onCreateAdHoc",
      };
    
    Ext.Array.remove(tbarItems, Ext.Array.findBy(tbarItems, function(item){
      return item.itemId === "detailsButton";
    }));

    tbarItems.splice(0, 0, closeBtn);
    tbarItems.splice(tbarItems.length - 1, 0, closeBtn, magicBtn);
    tbarItems.splice(1, 0, createBtn);
    // this.tbar = tbarItems;
    console.log("ChannelPanel initComponent", tbarItems);
    this.callParent(arguments);
  },
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
        me.unmask();
        if(Ext.isEmpty(obj)){
          NOC.info(__("No ad-hoc channels available"));
        } else{
          me.showMagicPanel();
          me.down("[xtype=invchannelmagic] grid").getStore().loadData(obj);
        }
      },
      failure: function(response){
        NOC.error(__("Failed to get data") + ": " + response.status);
        me.unmask();
      },
    });
  },
  //
  onChangeSelection: function(rowModel, selected){
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
  onDeselect: function(){
    this.down("#schemeContainer").removeAll(); 
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
  showChannelPanel: function(){
    this.down("#adhocInvChannelBtn").show();
    this.down("#zoomControl").show();
    this.down("#downloadSvgChannelBtn").show();
    this.down("#closeInvChannelBtn").hide();
    this.down("#createInvChannelBtn").hide(); 
    this.getLayout().setActiveItem(0);
  },
  //
  showMagicPanel: function(){
    this.getLayout().setActiveItem(1);
    this.down("#adhocInvChannelBtn").hide();
    this.down("#zoomControl").hide();
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
          NOC.launch("inv.channel", "history", {"args": [data.channel]});
          me.showChannelPanel();
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
