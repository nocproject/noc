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
          tooltip: __("Mark/Unmark"),
          getColor: function(cls, meta, r){
            return r.get("fav_status") ? NOC.colors.starred : NOC.colors.unstarred;
          },
          handler: "onFavItem",
        },
        {
          glyph: NOC.glyph.edit,
          tooltip: __("Edit"),
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
      width: 30,
      renderer: function(value, metaData, record){
        if(!Ext.isEmpty(value) && !Ext.isEmpty(record.get("job_id"))){
          return "<span class='job-status' "
            + "' data-record-id='" + record.get("job_id")
            + "' data-row-index='" + metaData.rowIndex + "'>"
            + NOC.render.JobStatusIcon(value) + "</span>"
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
      },
      searchField = {
        xtype: "searchfield",
        itemId: "filter",
        scope: this,
        handler: "onSearch",
        width: 300,
        minChars: 1,
        triggers: {
          clear: {
            cls: "x-form-clear-trigger",
            hidden: true,
            handler: function(field){
              field.setValue("");
              field.getTrigger("clear").hide();
            },
          },
        },
        listeners: {
          change: function(field, value){
            field.getTrigger("clear")[Ext.isEmpty(value) ? "hide" : "show"]();
          },
        },
      };
    // Make tbar
    Ext.Array.remove(tbarItems, Ext.Array.findBy(tbarItems, function(item){
      return item.itemId === "detailsButton";
    }));
    tbarItems.splice(0, 0, closeBtn);
    tbarItems.splice(2, 0, searchField);
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
    this.callParent(arguments);
    this.el.on("click", function(event, target){
      if(target.classList.contains("job-status")){
        var recordId = target.getAttribute("data-record-id"),
          rowIndex = target.getAttribute("data-row-index");
        this.handleEyeClick(recordId, rowIndex);
      }
    }, this, {delegate: ".job-status"});
  },
  //
  handleEyeClick: function(recordId, rowIndex){
    var tableView = this.down("grid").getView(),
      // eslint-disable-next-line @typescript-eslint/no-this-alias
      channelPanel = this,
      showGrid = function(){
        var panel = this.up();
        if(!Ext.isEmpty(tableView.getSelectionModel())){
          tableView.getSelectionModel().select(parseInt(rowIndex));
          channelPanel.showChannelPanel();
        }
        if(panel){
          panel.close();
        }
      };
    this.mask(__("Loading job panel ..."));
    NOC.launch("sa.job", "history", {
      "args": [recordId],
      "override": [
        {"showGrid": showGrid},
      ],
      "callback": Ext.bind(function(){
        tableView.getSelectionModel().select(parseInt(rowIndex));
        this.unmask();
      }, this),
    });

  },
  //
  getSelectedRow: function(){
    var grid = this.down("invchannelmagic").down("grid"),
      selectionModel = grid.getSelectionModel(),
      selectedRecord = selectionModel.getSelection()[0];
    return selectedRecord;
  },
  //
  onAdHoc: function(){
    var currentId = this.getViewModel().get("currentId"),
      url = "/inv/inv/" + currentId + "/plugin/channel/adhoc/",
      maskComponent = this.up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show(__("Fetching data for ad-hoc channels"));
    this.getViewModel().set("createInvChannelBtnDisabled", true);
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: this,
      success: function(response){
        var obj = Ext.decode(response.responseText);
        if(Ext.isEmpty(obj)){
          NOC.info(__("No ad-hoc channels available"));
        } else{
          this.down("[xtype=invchannelmagic] grid").getStore().loadData(obj);
          this.showMagicPanel();
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
    var schemeContainer = this.down("#schemeContainer");
    if(selected.length > 0){
      var recordData = selected[0].getData(),
        url = "/inv/channel/" + recordData.id + "/viz/",
        maskComponent = this.up("[appId=inv.inv]").maskComponent,
        messageId = maskComponent.show(__("Fetching data for draw scheme ..."));
      this.getViewModel().set("downloadSvgItemDisabled", false);
      Ext.Ajax.request({
        url: url,
        method: "GET",
        scope: this,
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
      this.getViewModel().set("downloadSvgItemDisabled", true);
      this.getViewModel().set("zoomDisabled", true);
      schemeContainer.setHtml("");
    }
  },
  //
  onCreateAdHoc: function(params){
    var currentId = this.getViewModel().get("currentId"),
      selectedRecord = this.getSelectedRow(),
      maskComponent = this.up("[appId=inv.inv]").maskComponent,
      message = Ext.isDefined(params.channel_id) ? __("Create new channel ..."): __("Update channel"),
      messageId = maskComponent.show(message); 
    Ext.Ajax.request({
      url: "/inv/inv/" + currentId + "/plugin/channel/adhoc/",
      method: "POST",
      scope: this,
      jsonData: Ext.apply(
        {endpoint: selectedRecord.get("start_endpoint"), controller: selectedRecord.get("controller")},
        params,
      ),
      success: function(response){
        var data = Ext.decode(response.responseText);
        if(data.status){
          NOC.info(data.msg);
          this.showChannelPanel(data.channel_id);
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
      formPanel = panel.down("form"), 
      selectedRecord = this.getSelectedRow();
    if(Ext.isEmpty(selectedRecord)){
      NOC.error(__("Please select a row"));
      return;
    }
    this.addFields(formPanel, selectedRecord);
    panel.show();
  },
  addFields: function(panel, record){
    panel.removeAll();    
    panel.add({
      xtype: "hiddenfield",
      name: "channel_id",
      value: record.get("channel_id"),
    });
    panel.add({
      xtype: "textfield",
      name: "name",
      fieldLabel: __("Name"),
      allowBlank: false,
      value: record.get("channel_name"),
    });
    this.addParamFields(panel, record.get("params") || []);
    panel.add({
      xtype: "checkbox",
      name: "dry_run",
      inputValue: true,
      uncheckedValue: false,
      fieldLabel: __("Dry Run"),
    });
  },
  //
  addParamFields: function(panel, params){
    Ext.Array.each(params, function(param){
      var field = {
        xtype: "textfield", // default field type
        name: "params." + param.name,
        fieldLabel: param.label || param.key || __("Unknowns"),
        disabled: param.readonly,
        value: param.value || "",
        allowBlank: !param.required || false,
      };

      if(Ext.isDefined(param.choices)){
        field.xtype = "combo";
        field.store = Ext.create("Ext.data.Store", {
          fields: ["id", "label"],
          data: param.choices,
        });
        field.displayField = "label";
        field.valueField = "id";
        field.queryMode = "local";
        field.editable = false;
        field.forceSelection = true;
      }

      panel.add(field);
    });
  },
  //
  onDeselect: function(){
    this.down("#schemeContainer").removeAll(); 
  },
  //
  onEdit: function(tableView, rowIndex){
    var record = tableView.getStore().getAt(rowIndex),
      id = record.get("id"),
      // eslint-disable-next-line @typescript-eslint/no-this-alias
      channelPanel = this,
      showGrid = function(){
        var panel = this.up();
        if(!Ext.isEmpty(tableView.getSelectionModel())){
          channelPanel.showChannelPanel();
          tableView.getSelectionModel().select(rowIndex);
        }
        if(panel){
          panel.close();
        }
      };
    NOC.launch("inv.channel", "history", {
      "args": [id],
      "override": [
        {"showGrid": showGrid},
      ],
      "callback": Ext.bind(function(){
        tableView.getSelectionModel().select(rowIndex);
      }, this),
    });
  },
  //
  onFavItem: function(grid, rowIndex){
    var r = grid.getStore().getAt(rowIndex),
      id = r.get("id"),
      action = r.get("fav_status") ? "reset" : "set",
      maskComponent = this.up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show(__("Favorite status updating ...")),
      url = "/inv/channel/favorites/item/" + id + "/" + action + "/";

    Ext.Ajax.request({
      url: url,
      method: "POST",
      scope: this,
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
    var activeItem = this.getLayout().getActiveItem();
    
    if(activeItem.xtype === "panel"){
      this.callParent();
    }

    if(activeItem.xtype === "invchannelmagic"){
      this.onAdHoc();
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
      store.loadData(obj.records || []);
      if(Ext.isEmpty(channelId)){
        return;
      }
      record = store.getById(channelId);
      if(record){
        grid.getSelectionModel().select(grid.getStore().indexOf(record));
        this.onChangeSelection(grid.getSelectionModel(), [record]);
      }
    });
  },
  //
  showMagicPanel: function(){
    var vm = this.getViewModel(),
      channelGrid = this.down("grid"),
      magicGrid = this.down("[xtype=invchannelmagic] grid");
    this.down("#adhocInvChannelBtn").hide();
    this.down("#zoomControl").hide();
    this.down("#downloadButton").hide();
    this.down("#createInvChannelBtn").show();
    this.down("#closeInvChannelBtn").show();
    vm.set("panelTitle", __("Create new channel"));
    vm.set("createInvChannelBtnText", __("Create"));
    this.getLayout().setActiveItem(1);
    if(!Ext.isEmpty(channelGrid.getSelection())){
      var record = magicGrid.getStore().findRecord("channel_id", channelGrid.getSelection()[0].id);
      if(record){
        magicGrid.getSelectionModel().select(record);
      }
    }
  },
  //
  onSearch: function(query){
    Ext.each(this.query("grid"), function(grid){
      var store = grid.getStore(),
        view = grid.getView();

      if(Ext.isEmpty(query)){
        store.clearFilter();
        view.emptyText = __("No records to display");
        return;
      }

      view.emptyText = __("No records found matching: ") + query;
    
      if(grid.itemId === "invChannelMagicGrid"){
        store.filterBy(function(record){
          var channelName = record.get("channel_name") || "",
            startEndpoint = record.get("start_endpoint") || "",
            endEndpoint = record.get("end_endpoint") || "";
        
          return channelName.toLowerCase().indexOf(query.toLowerCase()) > -1 ||
               startEndpoint.toLowerCase().indexOf(query.toLowerCase()) > -1 ||
               endEndpoint.toLowerCase().indexOf(query.toLowerCase()) > -1;
        });
      } else{
        store.filterBy(function(record){
          var name = record.get("name") || "",
            fromEndpoint = record.get("from_endpoint") || "",
            toEndpoint = record.get("to_endpoint") || "";
            
          return name.toLowerCase().indexOf(query.toLowerCase()) > -1 ||
               fromEndpoint.toLowerCase().indexOf(query.toLowerCase()) > -1 ||
               toEndpoint.toLowerCase().indexOf(query.toLowerCase()) > -1;
        });
      }
    
      view.refresh();
    });
  },
});
