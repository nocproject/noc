//---------------------------------------------------------------------
// inv.inv application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.Application");

Ext.define("NOC.inv.inv.Application", {
  extend: "NOC.core.Application",
  layout: "card",
  requires: [
    "NOC.inv.inv.NavModel",
    "NOC.inv.inv.CreateConnectionForm",
  ],
  initComponent: function(){
    var me = this;
    me.invPlugins = {};
    // Navigation tree
    me.defaultRoot = {
      text: __("."),
      children: [],
    };

    me.store = Ext.create("Ext.data.TreeStore", {
      model: "NOC.inv.inv.NavModel",
      sorters: "name",
      proxy: {
        type: "ajax",
        reader: "json",
        url: "/inv/inv/node/",
      },
      lazyFill: true,
    });

    me.navReloadButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.refresh,
      tooltip: __("Reload"),
      scope: me,
      handler: me.onReloadNav,
    });

    me.addButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.plus,
      tooltip: __("Add objects"),
      scope: me,
      handler: me.onAddObject,
    });

    me.createConnectionButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.plug,
      tooltip: __("Create connection"),
      scope: me,
      handler: me.onCreateConnection,
    });

    me.dashboardButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.line_chart,
      tooltip: __("Open Dashboard"),
      scope: me,
      disabled: true,
      handler: me.onOpenDashboard,
    });

    me.mapButton = Ext.create("Ext.button.Split", {
      text: __("Show Map"),
      glyph: NOC.glyph.globe,
      scope: me,
      handler: me.onShowMap,
      arrowVisible: false,
      disabled: true,
      menu: [], // Dynamically add items, after select node in navigation, method 'onSelectNav'
    });

    me.removeButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.minus,
      tooltip: __("Remove group"),
      scope: me,
      handler: me.onRemoveGroup,
    });

    me.navTree = Ext.create("Ext.tree.Panel", {
      store: me.store,
      autoScroll: true,
      rootVisible: false,
      useArrows: true,
      region: "west",
      split: true,
      loadMask: true,
      width: 300,
      displayField: "name",
      allowDeselect: true,
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        items: [
          me.navReloadButton,
          "-",
          me.addButton,
          me.removeButton,
          me.createConnectionButton,
          me.dashboardButton,
          me.mapButton,
        ],
      }],
      listeners: {
        scope: me,
        select: me.onSelectNav,
        deselect: me.onDeselect,
      },
      viewConfig: {
        plugins: {
          ptype: "treeviewdragdrop",
          ddGroup: "navi-tree-to-form",
        },
      },
    });
    me.navTree.getView().on("drop", me.onNavDrop, me);
    me.navTree.on('select', function(selModel){
      me.selectedModel = selModel;
    });

    me.tabPanel = Ext.create("Ext.tab.Panel", {
      region: "center",
      layout: "fit",
      border: false,
      scrollable: true,
      defaults: {
        scrollable: true,
      },
      items: [],
    });
    //
    me.connectionPanel = Ext.create("NOC.inv.inv.CreateConnectionForm", {
      app: me,
    });
    //
    me.mainPanel = Ext.create("Ext.panel.Panel", {
      layout: "border",
      items: [
        me.navTree,
        me.tabPanel,
      ],
    });
    me.ITEM_MAIN = me.registerItem(me.mainPanel);
    //
    me.ITEM_ADD = me.registerItem("NOC.inv.inv.AddObjectForm", {
      app: me,
    });
    //
    Ext.apply(me, {
      items: me.getRegisteredItems(),
      activeItem: me.ITEM_MAIN,
    });
    //
    me.callParent();
    // Process commands
    switch(me.getCmd()){
      case"history":
        me.restoreHistory(me.noc.cmd.args);
        return;
    }
  },
  //
  onReloadNav: function(){
    var me = this;
    me.store.reload({node: me.store.getRootNode()});
  },
  //
  runPlugin: function(objectId, pData){
    var me = this,
      plugin = Ext.create(pData.xtype, {app: me});
    me.tabPanel.add(plugin);
    me.invPlugins[pData.name] = plugin;
    Ext.Ajax.request({
      url: "/inv/inv/" + objectId + "/plugin/" + pData.name + "/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        plugin.preview(data, objectId);
      },
      failure: function(){
        NOC.error(__("Failed to get data for plugin") + " " + pData.name);
      },
    });
  },
  //
  addAppForm: function(parent, app, objectId){
    var me = this,
      url = "/" + app.replace(".", "/") + "/launch_info/",
      c;
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: me,
      success: function(response){
        var li = Ext.decode(response.responseText),
          params = {};
        Ext.merge(params, li.params);
        c = Ext.create("NOC." + app + ".Application", {
          noc: params,
          controller: me.controller,
        });
        c.loadById(objectId, function(record){
          c.onEditRecord(record);
        });
        parent.items.add(c);
      },
      failure: function(){
        NOC.error(__("Failed to launch application") + " " + app);
      },
    });
  },
  //
  onSelectNav: function(panel, record){
    var me = this,
      objectId = record.get("id"),
      plugins = record.get("plugins");
    me.addButton.setDisabled(!record.get("can_add"));
    me.removeButton.setDisabled(!record.get("can_delete"));
    me.dashboardButton.setDisabled(false);
    Ext.Ajax.request({
      url: "/inv/inv/" + objectId + "/map_lookup/",
      method: "GET",
      success: function(response){
        var defaultHandler, menuItems,
          data = Ext.decode(response.responseText);

        if(Ext.isEmpty(data)){
          me.mapButton.setDisabled(true);
          me.mapButton.setArrowVisible(false);
          return;
        }
        defaultHandler = data.filter(function(el){
          return el.is_default
        })[0];
        me.mapButton.setHandler(function(){
          NOC.launch("inv.map", "history", {
            args: defaultHandler.args,
          });
        }, me);
        me.mapButton.getMenu().removeAll();
        menuItems = data.filter(function(el){
          return!el.is_default
        }).map(function(el){
          return{
            text: el.label,
            handler: function(){
              NOC.launch("inv.map", "history", {
                args: el.args,
              })
            },
          }
        });
        Ext.Array.each(menuItems, function(item){
          me.mapButton.getMenu().add(item);
        });
        me.mapButton.setArrowVisible(menuItems.length);
        me.mapButton.setDisabled(false);
      },
      failure: function(){
        NOC.error(__("Failed get map menu"));
      },
    });
    me.invPlugins = {};
    me.tabPanel.removeAll();
    Ext.each(plugins, function(p){
      me.runPlugin(objectId, p);
    });
    me.tabPanel.setActiveTab(0);
    me.setHistoryHash(objectId);
  },
  //
  onDeselect: function(){
    var me = this;
    me.dashboardButton.setDisabled(true);
  },
  // Expand nav tree to object
  showObject: function(objectId, reload){
    var me = this;
    if(reload){
      me.store.on("load", function(){
        me.showObject(objectId)
      }, {
        scope: me,
        single: true,
      });
      me.onReloadNav();
    }
    Ext.Ajax.request({
      url: "/inv/inv/" + objectId + "/path/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText),
          path = [, me.navTree.getRootNode().get("id")];
        path = path.concat(data.map(function(v){
          return v.id
        }));
        me.navTree.selectPath(
          path.join("/"), "id", "/",
          function(success){
            if(!success){
              NOC.error(__("Failed to find node"));
            }
          }, me,
        );
      },
      failure: function(){
        NOC.error(__("Failed to get path"));
      },
    })
  },
  //
  onAddObject: function(){
    var sel,
      me = this,
      container = null;
    if(me.selectedModel){
      sel = me.selectedModel.getSelection();
    }
    if(!Ext.isEmpty(sel)){
      container = sel[0];
    }
    var i = me.showItem(me.ITEM_ADD);
    i.setTitle(__("Add object to ") + container.getPath("name"));
  },
  //
  onNavDrop: function(node, data, overModel, dropPosition){
    var me = this,
      objects = data.records.map(function(r){
        return r.get("id")
      });
    Ext.Ajax.request({
      url: "/inv/inv/insert/",
      method: "POST",
      jsonData: {
        objects: objects,
        container: overModel.get("id"),
        position: dropPosition,
      },
      scope: me,
      success: function(){
      },
      failure: function(){
        NOC.error(__("Failed to move"));
      },
    });
  },
  //
  onRemoveGroup: function(){
    var me = this,
      sm = me.navTree.getSelectionModel(),
      sel = sm.getSelection(),
      container = null;
    if(sel.length > 0){
      container = sel[0];
    }
    if(container){
      Ext.Msg.show({
        title: __("Remove group '") + container.get("name") + "'?",
        msg: "Would you like to remove group. All nested groups will be removed. All nested objects will be moved to Lost&Found folder",
        buttons: Ext.Msg.YESNO,
        glyph: NOC.glyph.question_circle,
        fn: function(rec){
          if(rec === "yes"){
            Ext.Ajax.request({
              url: "/inv/inv/remove_group/",
              method: "DELETE",
              jsonData: {
                container: container.get("id"),
              },
              scope: me,
              success: function(){
                me.store.reload({node: me.store.getRootNode()});
              },
              failure: function(){
                NOC.error(__("Failed to delete group"));
              },
            });
          }
        },
      });
    }
  },
  //
  restoreHistory: function(args){
    var me = this;
    me.showObject(args[0]);
  },
  //
  onCreateConnection: function(){
    var me = this;
    if(me.mainPanel.items.items.length > 2){
      me.mainPanel.remove(me.mainPanel.items.items[2], false);
    }
    me.mainPanel.add(me.connectionPanel);
  },
  //
  onOpenDashboard: function(){
    var me = this,
      sm = me.navTree.getSelectionModel(),
      sel = sm.getSelection(),
      container = null;

    if(sel.length > 0){
      container = sel[0];
    }

    if(container){
      window.open("/ui/grafana/dashboard/script/noc.js?dashboard=container&id=" + container.get("id") + "&orgId=1");
    }
  },
});
