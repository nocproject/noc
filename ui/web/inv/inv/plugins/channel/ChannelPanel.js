//---------------------------------------------------------------------
// inv.inv Channel Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.channel.ChannelPanel");

Ext.define("NOC.inv.inv.plugins.channel.ChannelPanel", {
  extend: "NOC.inv.inv.plugins.VizSchemePluginAbstract",
  title: __("Channels"),
  itemId: "channelPanel",
  layout: "card",
  requires: [
    "NOC.inv.inv.plugins.channel.MagicPanel",
    "NOC.inv.inv.plugins.channel.ParamsForm",
  ],
  viewModel: {
    data: {
      createInvChannelBtnDisabled: true,
      createInvChannelBtnText: __("Create"),
      panelTitle: __("Create new channel"),
    },
  },
  gridColumns: [
    {
      xtype: "glyphactioncolumn",
      width: 50,
      stopSelection: false,
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
    {
      text: __("Job"),
      dataIndex: "job_status",
      width: 120,
      renderer: function(value, metaData, record){
        if(!Ext.isEmpty(value) && !Ext.isEmpty(record.get("job_id"))){
          return "<i class='fas fa fa-eye' style='padding-right: 4px;cursor: pointer;' "
            + "title='" + __("View job")
            + "' data-record-id='" + record.get("job_id")
            + "' data-row-index='" + metaData.rowIndex + "'></i>"
            + NOC.render.JobStatus(value);
        }
      },
    },
  ],
  mainItems: [
    {
      xtype: "panel",      
      layout: {
        type: "vbox",
        align: "stretch",
      },
    },
    {
      xtype: "invchannelmagic",
      bind: {
        title: "{panelTitle}",
      },
      listeners: {
        magicselectionchange: "onMagicSelectionChange",
        magicopenparamsform: "onCreateBtn",
      },
    },
    {
      xtype: "invChannelParamsForm",
      bind: {
        title: "{panelTitle}",
      },
      listeners: {
        complete: "onCreateAdHoc",
      },
    },
  ],
  initComponent: function(){
    var parentItems = Ext.clone(this.items),
      tbarItems = Ext.clone(this.tbar),
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
        handler: "onAdHoc",
      },
      createBtn = {
        itemId: "createInvChannelBtn",
        glyph: NOC.glyph.plus,
        bind: {
          disabled: "{createInvChannelBtnDisabled}",
          text: "{createInvChannelBtnText}",
        },
        hidden: true,
        handler: "onCreateBtn",
      };
    // Make tbar
    Ext.Array.remove(tbarItems, Ext.Array.findBy(tbarItems, function(item){
      return item.itemId === "detailsButton";
    }));
    tbarItems.splice(0, 0, closeBtn);
    tbarItems.splice(tbarItems.length - 2, 0, magicBtn, createBtn);
    this.tbar = tbarItems;
    // Make items
    this.mainItems[0].items = parentItems;
    parentItems[0].listeners = {
      afterlayout: "afterGridRender",
      selectionchange: "onChangeSelection",
      deselect: "onDeselect",
    };
    this.items = this.mainItems;
    this.callParent(arguments);
  },
  //
  afterRender: function(){
    var me = this;
    me.callParent(arguments);
    me.el.on("click", function(event, target){
      if(target.classList.contains('fa-eye')){
        var recordId = target.getAttribute('data-record-id'),
          rowIndex = target.getAttribute('data-row-index');
        me.handleEyeClick(recordId, rowIndex);
      }
    }, me, {delegate: '.fa-eye'});
  },
  //
  handleEyeClick: function(recordId, rowIndex){
    var me = this,
      showGrid = function(){
        var panel = this.up();
        me.showChannelPanel();
        if(panel){
          panel.close();
        }
      };
    me.mask(__("Loading jpb panel ..."));
    NOC.launch("sa.job", "history", {
      "args": [recordId],
      "override": [
        {"showGrid": showGrid},
      ],
      "callback": Ext.bind(function(){
        var grid = this.down("grid");
        grid.getView().getSelectionModel().select(parseInt(rowIndex));
        this.unmask();
      }, me),
    });

  },
  //
  getSelectedRow: function(){
    var me = this,
      grid = me.down("invchannelmagic").down("grid"),
      selectionModel = grid.getSelectionModel(),
      selectedRecord = selectionModel.getSelection()[0];
    return selectedRecord;
  },
  //
  onAdHoc: function(){
    var me = this,
      currentId = me.getViewModel().get("currentId"),
      url = "/inv/inv/" + currentId + "/plugin/channel/adhoc/",
      maskComponent = me.up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show(__("Fetching data for ad-hoc channels"));
    me.getViewModel().set("createInvChannelBtnDisabled", true);
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
        }
      },
      failure: function(response){
        NOC.error(__("Failed to get data") + ": " + response.status);
      },
      callback: function(){
        maskComponent.hide(messageId);
      },
    });
  },
  //
  onChangeSelection: function(rowModel, selected){
    var me = this,
      schemeContainer = me.down("#schemeContainer");
    if(selected.length > 0){
      var recordData = selected[0].getData(),
        url = "/inv/channel/" + recordData.id + "/viz/",
        maskComponent = me.up("[appId=inv.inv]").maskComponent,
        messageId = maskComponent.show(__("Fetching data for draw scheme ..."));
      me.getViewModel().set("downloadSvgItemDisabled", false);
      Ext.Ajax.request({
        url: url,
        method: "GET",
        scope: me,
        success: function(response){
          var obj = Ext.decode(response.responseText);
          this.renderScheme(obj.data);
        },
        failure: function(response){
          NOC.error(__("Failed to get data") + ": " + response.status);
        },
        callback: function(){
          maskComponent.hide(messageId);
        },
      });
    } else{
      me.getViewModel().set("downloadSvgItemDisabled", true);
      me.getViewModel().set("zoomDisabled", true);
      schemeContainer.setHtml("");
    }
  },
  //
  onCreateAdHoc: function(params){
    var me = this,
      currentId = me.getViewModel().get("currentId"),
      selectedRecord = this.getSelectedRow(),
      maskComponent = me.up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show(__("Create new channel ...")); 
    Ext.Ajax.request({
      url: "/inv/inv/" + currentId + "/plugin/channel/adhoc/",
      method: "POST",
      jsonData: Ext.apply(
        {endpoint: selectedRecord.get("start_endpoint"), controller: selectedRecord.get("controller")},
        params,
      ),
      success: function(response){
        var data = Ext.decode(response.responseText);
        if(data.status){
          NOC.info(data.msg);
          me.showChannelPanel(data.channel_id);
        } else{
          NOC.error(data.msg);
        }
      },
      failure: function(response){
        NOC.error("Failure", response);
      },
      callback: function(){
        maskComponent.hide(messageId);
      },
    });
  },
  //
  onCreateBtn: function(){
    var panel = this.down("invChannelParamsForm"),
      form = panel.down("form").getForm(),
      selectedRecord = this.getSelectedRow();
    if(Ext.isEmpty(selectedRecord)){
      NOC.error(__("Please select a row"));
      return;
    }
    if(Ext.isEmpty(selectedRecord.get("channel_id"))){
      form.reset();
    } else{
      form.setValues({
        channel_id: selectedRecord.get("channel_id"),
        name: selectedRecord.get("channel_name"),
      });
    }
    panel.show();
  },
  //
  onDeselect: function(){
    this.down("#schemeContainer").removeAll(); 
  },
  //
  onEdit: function(tableView, rowIndex){
    var me = this,
      record = tableView.getStore().getAt(rowIndex),
      id = record.get("id"),
      showGrid = function(){
        var panel = this.up();
        me.showChannelPanel();
        if(panel){
          panel.close();
        }
      };
    me.mask(__("Loading channel panel ..."));
    NOC.launch("inv.channel", "history", {
      "args": [id],
      "override": [
        {"showGrid": showGrid},
      ],
      "callback": Ext.bind(function(){
        tableView.getSelectionModel().select(rowIndex);
        this.unmask();
      }, me),
    });
  },
  //
  onFavItem: function(grid, rowIndex){
    var me = this,
      r = grid.getStore().getAt(rowIndex),
      id = r.get("id"),
      action = r.get("fav_status") ? "reset" : "set",
      maskComponent = me.up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show(__("Favorite status updating ...")),
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
      failure: function(response){
        NOC.error(__("Failed to get data") + ": " + response.status);
      },
      callback: function(){
        maskComponent.hide(messageId);
      },
    });
  },
  //
  onMagicSelectionChange: function(disable, text, title){
    var vm = this.getViewModel();
    vm.set("createInvChannelBtnDisabled", disable);
    vm.set("createInvChannelBtnText", text);
    vm.set("panelTitle", title);
  },
  //
  onReload: function(){
    var me = this,
      activeItem = me.getLayout().getActiveItem();
    
    if(activeItem.xtype === "panel"){
      me.callParent();
    }

    if(activeItem.xtype === "invchannelmagic"){
      me.onAdHoc();
    }
  },
  //
  showChannelPanel: function(channelId){
    this.down("#adhocInvChannelBtn").show();
    this.down("#zoomControl").show();
    this.down("#downloadButton").show();
    this.down("#closeInvChannelBtn").hide();
    this.down("#createInvChannelBtn").hide(); 
    this.getLayout().setActiveItem(0);
    this.getData(function(response){
      var record,
        obj = Ext.decode(response.responseText),
        grid = this.down("grid"),
        store = grid.getStore();        
      store.loadData(obj.records);
      if(Ext.isEmpty(channelId)){
        return;
      }
      record = store.getById(channelId);
      if(record){
        grid.getSelectionModel().select(grid.getStore().indexOf(record));
      }
    });
  },
  //
  showMagicPanel: function(){
    var vm = this.getViewModel();
    this.down("#adhocInvChannelBtn").hide();
    this.down("#zoomControl").hide();
    this.down("#downloadButton").hide();
    this.down("#createInvChannelBtn").show();
    this.down("#closeInvChannelBtn").show();
    vm.set("panelTitle", __("Create new channel"));
    vm.set("createInvChannelBtnText", __("Create"));
    this.getLayout().setActiveItem(1);
  },
});
