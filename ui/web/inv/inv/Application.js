//---------------------------------------------------------------------
// inv.inv application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.Application");

Ext.define("NOC.inv.inv.Application", {
  extend: "NOC.core.Application",
  layout: "card",
  requires: [
    "NOC.inv.inv.CreateConnectionForm",
    "NOC.inv.inv.MaskComponent",
    "NOC.inv.inv.NavModel",
    "NOC.inv.inv.NavSearch",
  ],
  pollingTaskId: undefined,
  pollingInterval: 2000,
  //
  viewModel: {
    data: {
      autoReload: false,
      autoReloadIcon: "xf05e", // NOC.glyph.ban
      autoReloadText: __("Auto reload : OFF"),
      icon: "<i class='fa fa-fw' style='width:16px;'></i>",
    },
  },
  naviTreeMessageStack: [],
  //
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
      proxy: {
        type: "ajax",
        reader: "json",
        url: "/inv/inv/node/",
      },
      lazyFill: true,
      listeners: {
        scope: me,
        beforeload: function(store, operation){
          if(this.navTree){
            let naviTreeMessageId = this.maskNaviTree.show(__("Loading..."));
            operation.messageId = naviTreeMessageId;
            this.naviTreeMessageStack.push({
              id: naviTreeMessageId,
              operation: operation,
            });
          }
        },
        load: function(store, records, successful, operation){
          if(this.navTree && this.navTree.isVisible() && !Ext.isEmpty(operation.messageId)){
            this.hideNaviTreeMessage(operation.messageId);
          }
        },
      },
    });

    me.navReloadButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.refresh,
      tooltip: __("Reload"),
      scope: me,
      handler: me.onReloadNav,
    });

    me.menu = Ext.create("Ext.menu.Menu", {
      plain: true,
      items: [
        {
          glyph: NOC.glyph.plus,
          itemId: "invNavContextMenuAddItem",
          text: __("Add objects"),
          scope: me,
          handler: me.onAddObject,
        },
        {
          glyph: NOC.glyph.copy,
          text: __("Clone"),
          scope: me,
          handler: me.onClone,
        },
        {
          glyph: NOC.glyph.plug,
          text: __("Connect"),
          scope: me,
          disabled: false,
          handler: me.onCreateConnection,
        },
        {
          xtype: "menuseparator",
        },
        {
          glyph: NOC.glyph.line_chart,
          itemId: "invNavContextMenuShowDashboardItem",
          text: __("Show Dashboard"),
          scope: me,
          disabled: false,
          handler: me.onOpenDashboard,
        },
        {
          xtype: "menuseparator",
        },
        {
          glyph: NOC.glyph.trash_o,
          itemId: "invNavContextMenuRemoveAllConnectionItem",
          text: __("Remove all connections"),
          scope: me,
          cls: "noc-remove-menu-item",
          handler: me.onRemoveAllConnections,
        },
        {
          glyph: NOC.glyph.trash_o,
          itemId: "invNavContextMenuRemoveItem",
          text: __("Delete"),
          scope: me,
          cls: "noc-remove-menu-item",
          handler: me.onRemoveGroup,
        },
      ],
      listeners: {
        afterrender: function(menu){
          menu.getEl().on("keydown", function(e){
            if(e.getKey() === e.ESC){
              me.isMenuShow = false;
              menu.hide();
            }
          });
        },
      },
    });

    me.isMenuShow = false;

    me.navTree = Ext.create("Ext.tree.Panel", {
      store: me.store,
      autoScroll: true,
      animate: false,
      rootVisible: false,
      useArrows: true,
      region: "west",
      split: true,
      width: 300,
      displayField: "name",
      allowDeselect: true,
      hideHeaders: true,
      stickyNode: "sticky-node",
      zIndex: 100,
      rowHeight: 36, // for noc theme
      maxStickyLevel: 1,
      bufferedRenderer: false,
      columns: [
        {
          xtype: "treecolumn", // This is a mandatory column to display a tree
          dataIndex: "name",
          flex: 1,
          cellTpl: [
            '<div style="display:flex;justify-content:space-between;">',
            '  <div style="text-overflow: ellipsis;overflow: hidden;">',
            '  <tpl for="lines">',
            '    <div class="{parent.childCls} {parent.elbowCls}-img ',
            '    {parent.elbowCls}-<tpl if=".">line<tpl else>empty</tpl>" role = "presentation"></div>',
            "  </tpl>",
            '  <div class="{childCls} {elbowCls}-img ',
            '    {elbowCls}<tpl if= " isLast">-end</tpl><tpl if="expandable">-plus {expanderCls}</tpl>" role = "presentation" ></div >',
            '  <tpl if="checked !== null">',
            '    <input type="button" {ariaCellCheckboxAttr} class="{childCls} {checkboxCls} <tpl if= " checked" > {checkboxCls}-checked</tpl> "/>',
            "  </tpl>",
            '  <tpl if="this.isAlarmed(record)">',
            '    <i class="fa fa-exclamation-triangle" style="font-size: 16px; color: {[NOC.colors.no]};"></i>',
            '  <tpl elseif="glyphCls"><i class="{glyphCls}" style="font-size: 16px"></i>',
            '  <tpl else><div role="presentation" class="{childCls} {baseIconCls} {baseIconCls}-<tpl if="leaf">leaf<tpl else>parent</tpl> ',
            '     {iconCls}"<tpl if="icon">style="background - image: url({icon})"</tpl>></div></tpl>',
            '  <tpl if="href"><a href="{href}" role="link" target="{hrefTarget}" class="{textCls} {childCls}">{value}</a>',
            '  <tpl else><span class="{textCls} {childCls}">{value}</span></tpl>',
            "  </div>",
            '  <button class="cell-button" style="display: none;">...</button>',
            "</div>",
            {
              isAlarmed: function(record){
                return record.get("is_alarm") && me.getViewModel().get("autoReload");
              }, 
            },
          ],
        },
      ],
      dockedItems: [{
        xtype: "container",
        dock: "top",
        layout: {
          type: "vbox",
          align: "stretch",
        },
        items: [
          {
            xtype: "toolbar",
            items: [
              me.navReloadButton,
              {
                text: __("Reload"),
                iconAlign: "right",
                enableToggle: true,
                bind: {
                  glyph: "{autoReloadIcon}",
                  tooltip: "{autoReloadText}",
                  pressed: "{autoReload}",
                },
                listeners: {
                  scope: me,
                  toggle: me.onAutoReloadToggle,
                },
              },
              "->",
              {
                glyph: NOC.glyph.plus,
                tooltip: __("Add objects"),
                itemId: "addObjectDock",
                disabled: false,
                scope: me,
                handler: me.onAddObject,
              },
              {
                xtype: "tbtext",
                padding: "3 0 0 4",
                bind: {
                  html: "{icon}",
                },
              },
            ],
          },
          {
            xtype: "toolbar",
            items: [
              {
                xtype: "searchcombo",
                width: "100%",
                listeners: {
                  scope: this,
                  invPathSelected: function(pathId){
                    this.showObject(pathId, false);
                  },
                },
              },
            ],
          },
        ],
      }],
      listeners: {
        scope: me,
        beforeselect: me.onBeforeSelect,
        select: me.onSelectNav,
        deselect: me.onDeselect,
        afterrender: function(treePanel){
          treePanel.getEl().on("click", function(event, target){
            if(Ext.fly(target).hasCls("cell-button")){
              var record = treePanel.getView().getRecord(target.closest(".x-grid-row")),
                objectId = record.get("id");
 
              if(me.isMenuShow){
                me.isMenuShow = !me.isMenuShow;
                me.menu.hide();
                return;
              }
              Ext.Ajax.request({
                url: "/inv/inv/" + objectId + "/map_lookup/",
                method: "GET",
                success: function(response){
                  var defaultHandler, menuItems,
                    mapItemPosition = 5,
                    data = Ext.decode(response.responseText),
                    mapMenuItem = me.menu.down("#invNavContextMenuMapItem"),
                    addMenuItem = me.menu.down("#invNavContextMenuAddItem"),
                    removeMenuItem = me.menu.down("#invNavContextMenuRemoveItem"),
                    removeAllConnectionMenuItem = me.menu.down("#invNavContextMenuRemoveAllConnectionItem");
                    
                  addMenuItem.setDisabled(!record.get("can_add"));
                  removeMenuItem.setDisabled(!record.get("can_delete"));
                  removeAllConnectionMenuItem.setDisabled(!record.get("can_delete"));
                  if(mapMenuItem){
                    me.menu.remove(mapMenuItem);
                  }

                  if(Ext.isEmpty(data)){
                    me.menu.insert(mapItemPosition, {
                      itemId: "invNavContextMenuMapItem",
                      text: __("Show Map"),
                      glyph: NOC.glyph.globe,
                      disabled: true,
                    });
                    return;
                  }
                  defaultHandler = data.filter(function(el){
                    return el.is_default
                  })[0];
                  menuItems = data.filter(function(el){
                    return !el.is_default
                  }).map(function(el){
                    return {
                      text: el.label,
                      handler: function(){
                        NOC.launch("inv.map", "history", {
                          args: el.args,
                        })
                      },
                    }
                  });
                  // mapMenuItem
                  if(menuItems.length){
                    me.menu.insert(mapItemPosition, {
                      itemId: "invNavContextMenuMapItem",
                      text: __("Show Map"),
                      glyph: NOC.glyph.globe,
                      menu: menuItems,
                    });
                  } else{
                    me.menu.insert(mapItemPosition, {
                      itemId: "invNavContextMenuMapItem",
                      text: __("Show Map"),
                      glyph: NOC.glyph.globe,
                      handler: function(){
                        NOC.launch("inv.map", "history", {
                          args: defaultHandler.args,
                        });
                      },
                    });
                  }
                },
                failure: function(){
                  NOC.error(__("Failed get map menu"));
                },
              });
              me.isMenuShow = true;
              me.menu.showAt(event.getXY());
            }
          }, null, {delegate: ".cell-button"});
        },
        beforecellclick: function(treePanel, td, cellIndex, record, tr, rowIndex, e){
          return !Ext.fly(e.target).hasCls("cell-button");
        },
        beforecelldblclick: function(){
          return false;
        },
        viewready: function(treePanel){
          var view = treePanel.getView(),
            nodes = view.getNodes(0, 0);
          if(nodes.length > 0){
            treePanel.rowHeight = Ext.fly(nodes[0]).getHeight();
          }
          Ext.fly(view.getEl().dom).down(".x-grid-item-container").setStyle("overflow", "unset");
          treePanel.createStickyCss(1);
        },
      },
      createStickyCss: function(level){
        var css = `table.x-grid-item:has(tr.${this.stickyNode}-${level}) { position: sticky; top: ${(level - 1) * this.rowHeight}px; z-index: ${this.zIndex}; }`;
        Ext.util.CSS.createStyleSheet(css);
        this.maxStickyLevel = level;
      },
      viewConfig: {
        plugins: {
          ptype: "treeviewdragdrop",
          ddGroup: "navi-tree-to-form",
        },
        getRowClass: function(record){
          var me = this.up("treepanel"),
            depth = parseInt(record.get("depth"), 10),
            isNewLevel = depth > me.maxStickyLevel;
          
          if(isNewLevel){
            me.createStickyCss(depth);
          }
          return `${me.stickyNode}-${depth}`;
        },
      },
    });
    me.navTree.getView().on("beforedrop", me.onNavDrop, me);
    me.maskNaviTree = Ext.create("NOC.inv.inv.MaskComponent", {
      maskedComponent: me.navTree,
    });
    me.tabPanel = Ext.create("Ext.tab.Panel", {
      layout: "fit",
      border: false,
      scrollable: true,
      defaults: {
        scrollable: true,
      },
      items: [],
      listeners: {
        scope: me,
        beforetabchange: me.onBeforeTabChange,
      },
    });
    me.maskComponent = Ext.create("NOC.inv.inv.MaskComponent", {
      maskedComponent: me.tabPanel,
    });
    //
    me.connectionPanel = Ext.create("NOC.inv.inv.CreateConnectionForm", {
      app: me,
      listeners: {
        scope: me,
        reloadInvNav: me.onReloadNav, 
      },
    });
    //
    me.workPanel = Ext.create("Ext.panel.Panel", {
      layout: "card",
      region: "center",
      activeItem: 0,
      items: [
        me.tabPanel,
        me.connectionPanel,
      ],
    });
    //
    me.mainPanel = Ext.create("Ext.panel.Panel", {
      layout: "border",
      items: [
        me.navTree,
        me.workPanel,
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
      case "history":
        me.restoreHistory(me.noc.cmd.args);
        break;
    }
    this.subscribeToEvents();
  },
  //
  onReloadNav: function(){
    var me = this,
      sel = me.navTree.getSelection();

    me.navTree.getSelectionModel().deselectAll();
    me.store.reload({
      node: me.store.getRootNode(),
      callback: function(){
        if(!Ext.isEmpty(sel)){
          this.showObject(sel[0].get("id"), false);
        } else{
          this.onDeselect();
        }
      },
      scope: me,
    });
  },
  //
  runPlugin: function(objectId, pData, index){
    var me = this,
      messageId = me.maskComponent.show("loading", [pData.name]);

    Ext.Loader.require(pData.xtype, function(){
      var plugin = Ext.create(pData.xtype, {app: this});
      this.tabPanel.insert(index, plugin);
      this.invPlugins[pData.name] = plugin;
      plugin.pluginName = pData.name;
      me.maskComponent.hide(messageId);
      this.loadedPlugins++;
      if(this.loadedPlugins === this.maxPlugins){
        if(this.currentPlugin && this.invPlugins[this.currentPlugin]){
          this.tabPanel.setActiveTab(this.invPlugins[this.currentPlugin]);
        } else{
          this.tabPanel.setActiveTab(0);
        }
      }
    }, this);
  },
  //
  addAppForm: function(parent, app, objectId){
    var me = this,
      url = "/" + app.replace(".", "/") + "/launch_info/",
      messageId = me.maskComponent.show("processing", [app]),
      c;
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: me,
      success: function(response){
        var li = Ext.decode(response.responseText),
          xtype = "NOC." + app + ".Application",
          params = {};
        Ext.merge(params, li.params);
        Ext.Loader.require(xtype, function(){
          c = Ext.create(xtype, {
            noc: params,
            controller: me.controller,
          });
          c.loadById(objectId, function(record){
            c.onEditRecord(record);
          });
          parent.add(c);
          me.maskComponent.hide(messageId);
        });
      },
      failure: function(){
        me.maskComponent.hide(messageId);
        NOC.error(__("Failed to launch application") + " " + app);
      },
    });
  },
  onBeforeTabChange: function(tabPanel, currentPanel, oldPanel){
    var me = this,
      objectId = me.selectedObjectId,
      pluginName = currentPanel.pluginName,
      messageId = me.maskComponent.show("fetching", [pluginName]);
    if(oldPanel && !Ext.isEmpty(oldPanel.messageId)){
      me.maskComponent.hide(me.messageId);
    }
    if(oldPanel && !Ext.isEmpty(oldPanel.timer)){
      Ext.TaskManager.stop(oldPanel.timer);
      oldPanel.timer = null;
    }
    Ext.Ajax.request({
      url: "/inv/inv/" + objectId + "/plugin/" + pluginName + "/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        currentPanel.preview(data, objectId);
      },
      failure: function(){
        NOC.error(__("Failed to get data for plugin") + " " + pluginName);
      },
      callback: function(){
        me.maskComponent.hide(messageId);
      },
    });
  },
  //
  onBeforeSelect: function(){
    var activeTab = this.tabPanel.getActiveTab();
    if(activeTab && activeTab.pluginName){
      this.currentPlugin = activeTab.pluginName;
    }
  },
  //
  onSelectNav: function(rowModel, record){
    var me = this,
      objectId = record.get("id"),
      node = rowModel.view.getNode(record),
      plugins = record.get("plugins");
    if(node){
      var btn = node.querySelector("button");
      if(btn){
        btn.style.display = "block";
      }
    }
    me.maxPlugins = plugins.length;
    me.loadedPlugins = 0;
    me.down("#addObjectDock").hide();
    me.selectedObjectId = objectId;
    me.invPlugins = {};
    me.tabPanel.removeAll();
    Ext.each(plugins, function(p, index){
      me.runPlugin(objectId, p, index);
    });
    me.isMenuShow = false;
    me.setHistoryHash(objectId);
    if(me.currentPlugin && me.invPlugins[me.currentPlugin]){
      me.tabPanel.setActiveTab(me.invPlugins[me.currentPlugin]);
      return;
    }
    me.tabPanel.setActiveTab(0);
  },
  //
  onDeselect: function(rowModel, record){
    this.down("#addObjectDock").show();
    Ext.ComponentQuery.query("tooltip#schemeBalloon, tooltip#mapBalloon").forEach(function(tooltip){
      tooltip.destroy();
    });
    if(rowModel){
      var node = rowModel.view.getNode(record);
      if(node){
        node.querySelector("button").style.display = "none";
      }
    }
    this.tabPanel.suspendLayouts();
    this.tabPanel.removeAll();
    this.tabPanel.resumeLayouts();
    this.setHistoryHash();
  },
  // Expand nav tree to object
  showObject: function(objectId, reload){
    var me = this;
    if(reload){
      me.onReloadNav();
    }
    Ext.Ajax.request({
      url: "/inv/inv/" + objectId + "/path/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText),
          path = Ext.Array.reduce(data, function(acc, curr){
            return acc + "/" + curr.id
          }, "/" + me.navTree.getRootNode().get("id"));
        
        me.navTree.selectPath(
          path, "id", "/",
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
    
    if(me.navTree.getSelectionModel().hasSelection()){
      sel = me.navTree.getSelectionModel().getSelection();
    }
    if(!Ext.isEmpty(sel)){
      container = sel[0];
    }
    
    var i = me.showItem(me.ITEM_ADD),
      formStore = i.down("grid").getStore();
    formStore.removeAll();
    formStore.add({});
    i.setContainer(container);
  },
  //
  onNavDrop: function(node, data, overModel, dropPosition, dropHandlers){
    var itemId,
      me = this;
    
    if(!Ext.isEmpty(data.records)){
      itemId = data.records[0].get("id");
      dropHandlers.wait = true;
      Ext.Ajax.request({
        url: "/inv/inv/attach/",
        method: "POST",
        jsonData: {
          item: itemId,
          container: overModel.get("id"),
        },
        scope: me,
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(Object.hasOwn(data, "choices")){
            // open popup with choices
            Ext.create("Ext.window.Window", {
              autoShow: true,
              title: __("Attach to"),
              height: 400,
              width: 800,
              layout: "fit",
              modal: true,
              items: [
                {
                  xtype: "form",
                  bodyPadding: 10,
                  layout: "anchor",
                  scrollable: true,
                  defaults: {
                    anchor: "100%",
                    labelWidth: 200,
                  },
                  items: [
                    {
                      xtype: "treepanel",
                      displayField: "name",
                      rootVisible: false,
                      useArrows: true,
                      allowDeselect: true,
                      store: Ext.create("Ext.data.TreeStore", {
                        root: data.choices,
                      }),
                      listeners: {
                        beforeselect: function(tree, record){
                          return record.get("leaf");
                        },
                        select: function(){
                          this.up("form").down("#attachBtn").setDisabled(false);
                        },
                        deselect: function(){
                          this.up("form").down("#attachBtn").setDisabled(true);
                        },
                      },
                    },
                  ],
                  buttons: [
                    {
                      text: __("Attach"),
                      itemId: "attachBtn",
                      disabled: true,
                      glyph: NOC.glyph.check,
                      handler: function(){
                        var tree = this.up("form").down("treepanel"),
                          sel = tree.getSelectionModel().getSelection();
                        if(sel.length > 0){
                          Ext.Ajax.request({
                            url: "/inv/inv/attach/",
                            method: "POST",
                            jsonData: {
                              item: itemId,
                              container: overModel.get("id"),
                              choice: sel[0].get("id"),
                            },
                            scope: this,
                            success: function(response){
                              var data = Ext.decode(response.responseText);
                              NOC.info(data.message); 
                              this.up("window").close();
                              me.onReloadNav();
                            },
                            failure: function(response){
                              var data = Ext.decode(response.responseText);
                              dropHandlers.cancelDrop();
                              if(data.status === false){
                                NOC.error(__(data.message));
                                return;
                              }
                              NOC.error(__("HTTP request failed."));
                            },
                          });
                        }
                      },
                    },
                    {
                      text: __("Cancel"),
                      glyph: NOC.glyph.times,
                      handler: function(){
                        dropHandlers.cancelDrop();
                        this.up("window").close();
                      },
                    },
                  ],
                },
              ],
            });
          } else if(Object.hasOwn(data, "status") && data.status){
            me.onReloadNav(); 
            NOC.info(data.message);
          }
        },
        failure: function(response){
          var data = Ext.decode(response.responseText);
          dropHandlers.cancelDrop();
          if(data.status === false){
            NOC.error(data.message);
            return;
          }
          NOC.error(__("HTTP request failed."));
        },
      });
    }
  },
  //
  getSelectedObject: function(){
    var me = this,
      sm = me.navTree.getSelectionModel(),
      sel = sm.getSelection(),
      container = null;
    if(sel.length > 0){
      container = sel[0];
    }
    return container;
  },
  //
  onRemoveGroup: function(){
    var me = this,
      container = me.getSelectedObject();
    if(container){
      var hasNoChildren = container.get("expandable") === false,
        parent= container.parentNode,
        hasNoParent = Ext.isEmpty(parent.get("name")),
        title = __("Remove group '") + container.get("name") + "'?";
      
      if(hasNoChildren){
        Ext.Msg.show({
          title: title,
          msg: __("Would you like to remove group?"),
          buttons: Ext.Msg.YESNO,
          glyph: NOC.glyph.question_circle,
          fn: function(rec){
            if(rec === "yes"){
              me.navTree.getSelectionModel().deselect(container);
              me.removeGroup(container, {container: container.id, action: "r"}, me);
            }
          },
        });
      } else{
      // Object has children
        var dialog = Ext.create("Ext.window.Window", {
          autoShow: true,
          title: title,
          height: 250,
          width: 500,
          layout: "form",
          modal: true,
          items: [
            {
              xtype: "radiogroup",
              columns: 1,
              vertical: true,
              items: [
                {
                  boxLabel: __("Move nested objects to") + " " + parent.get("name"),
                  name: "action",
                  inputValue: "p",
                  disabled: hasNoParent,
                },
                {boxLabel: __("Move nested objects to Lost&Found"), name: "action", inputValue: "l"},
                {boxLabel: __("Remove nested objects"), name: "action", inputValue: "r"},
              ],
              listeners: {
                change: function(radio, newValue){
                  dialog.down("#removeBtn").setDisabled(false);
                  dialog.down("#keepConnections").setDisabled(
                    !["p", "l"].includes(newValue.action));
                },
              },
            },
            {
              xtype: "checkbox",
              itemId: "keepConnections",
              disabled: true,
              boxLabel: __("Keep connections"),
            },
          ],
          buttons: [
            {
              text: __("Remove Group"),
              glyph: NOC.glyph.minus,
              itemId: "removeBtn",
              disabled: true,
              handler: function(){
                var options = {
                    container: container.id,
                    action: dialog.down("radiogroup").getValue().action,
                  },
                  keepConnectionsField = dialog.down("#keepConnections");
                if(!keepConnectionsField.isDisabled()){
                  options.keep_connections = keepConnectionsField.checked;
                }
                me.removeGroup(container, dialog, options, me);
              },
            },
            {
              text: __("Cancel"),
              glyph: NOC.glyph.times,
              handler: function(){
                dialog.close();
              },
            },
          ],
        }); 
      }
    }
  },
  onRemoveAllConnections: function(){
    Ext.Msg.show({
      title: __("Remove all connections"),
      message: __("Do you want to remove all connections within object? This operation cannot be undone!"),
      buttons: Ext.Msg.YESNO,
      icon: Ext.Msg.QUESTION,
      scope: this,
      fn: function(btn){
        if(btn === "yes"){
          var selectedObject = this.getSelectedObject();
          if(selectedObject){
            Ext.Ajax.request({
              url: "/inv/inv/remove_connections/",
              method: "DELETE",
              jsonData: {container: selectedObject.id},
              success: function(response){
                var data = Ext.decode(response.responseText);
                if(data.status){
                  NOC.info(__("Connections removed"));
                } else{
                  NOC.error(data.message);
                }
              },
              failure: function(response){
                NOC.error(__("Failed to remove connections : ") + response.responseText);
              },
            });
          }
        }
      },
    });
  },
  //
  restoreHistory: function(args){
    var me = this;
    me.showObject(args[0]);
  },
  //
  onCreateConnection: function(){
    var me = this,
      sm = me.navTree.getSelectionModel(),
      selected = sm.getSelection();
    
    if(selected.length > 0){
      me.workPanel.setActiveItem(me.connectionPanel);
      me.connectionPanel.onDrop({dragData: {records: selected} });
    }
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
  //
  onClone: function(){
    var me = this,
      dialog = Ext.create("Ext.window.Window", {
        title: __("Clone object?"),
        modal: true,
        width: 250,
        height: 160,
        layout: "vbox",
        autoShow: true,
        items: [
          {
            xtype: "checkbox",
            boxLabel: __("Clone connections"),
            padding: 10,
            itemId: "cloneConnectionsCheckbox",
          },
        ],
        buttons: [
          {
            text: __("Clone"),
            glyph: NOC.glyph.copy,
            handler: function(){
              var sel, cloneConnections = dialog.down("#cloneConnectionsCheckbox").checked,
                container = null;
              if(me.navTree.getSelectionModel().hasSelection()){
                sel = me.navTree.getSelectionModel().getSelection();
              }
              if(!Ext.isEmpty(sel)){
                container = sel[0];
              }
              Ext.Ajax.request({
                url: "/inv/inv/clone/",
                method: "POST",
                jsonData: {
                  container: container.id,
                  clone_connections: cloneConnections,
                },
                success: function(response){
                  var data = Ext.decode(response.responseText);
                  if(data.status){
                    var sm = me.navTree.getSelectionModel(),
                      sel = sm.getSelection(),
                      path = sel[0].getPath();

                    sm.deselect(sel[0]);
                    me.store.reload({
                      node: me.store.getRootNode(),
                      callback: function(){
                        if(!Ext.isEmpty(sel)){
                          me.navTree.selectPath(path.replace(me.selectedObjectId, data.object), "id");
                          me.selectedObjectId = data.object;
                        }
                      },
                      scope: me,
                    });
                    NOC.info(data.message);
                  } else{
                    NOC.error(data.message);
                  }
                },
                failure: function(){
                  NOC.error(__("Failed to clone object."));
                },
              });

              dialog.close();
            },
          },
          {
            text: __("Cancel"),
            glyph: NOC.glyph.times,
            handler: function(){
              dialog.close();
            },
          },
        ],
      });
  },
  //
  removeGroup: function(container, dialog, data, me){
    Ext.Ajax.request({
      url: "/inv/inv/remove_group/",
      method: "DELETE",
      jsonData: data,
      scope: me,
      success: function(){
        var parentId = container.get("parentId");
        if(parentId === "root"){
          me.store.reload({node: me.store.getRootNode()});
          me.tabPanel.removeAll();
          me.setHistoryHash();
          me.down("#addObjectDock").show(); 
        } else{
          me.store.reload({
            node: me.store.getRootNode(),
            callback: function(){
              var path = container.getPath().replace("/" + container.id, "");
              me.navTree.expandPath(path, "id");
              me.navTree.selectPath(path, "id");
            },
            scope: me,
          });
          me.setHistoryHash(parentId);
        }
        if(dialog){
          dialog.close();
        }
      },
      failure: function(){
        if(dialog){
          dialog.close();
        }
        NOC.error(__("Failed to delete group"));
      },
    });
  },
  //
  hideNaviTreeMessage: function(messageId){
    this.maskNaviTree.hide(messageId);
    this.naviTreeMessageStack = this.naviTreeMessageStack.filter(item => item.id !== messageId);
  },
  //
  onAutoReloadToggle: function(self){
    this.getViewModel().set("autoReload", self.pressed);
    this.autoReloadIcon(self.pressed);
    this.autoReloadText(self.pressed);
    if(this.getViewModel()){
      this.getViewModel().set("icon", this.generateIcon(self.pressed, "circle", NOC.colors.yes, __("online")));
    }
    if(self.pressed){
      this.startPolling();
    } else{
      this.stopPolling();
      this.store.getData().filterBy(function(item){return item.isVisible}).items.forEach(function(item){
        item.set("is_alarm", false);
      });
      this.navTree.getView().refresh(); 
    }
  },
  //
  autoReloadIcon: function(isReloading){
    //  NOC.glyph.refresh or NOC.glyph.ban
    this.getViewModel().set("autoReloadIcon", isReloading ? "xf021" : "xf05e");
  },
  //
  autoReloadText: function(isReloading){
    this.getViewModel().set("autoReloadText", __("Auto reload : ") + (isReloading ? __("ON") : __("OFF")));
  },
  //
  generateIcon: function(isUpdatable, icon, color, msg){
    if(isUpdatable){
      return `<i class='fa fa-${icon}' style='color:${color};width:16px;' data-qtip='${msg}'></i>`;
    }
    return "<i class='fa fa-fw' style='width:16px;'></i>";
  },
  //
  startPolling: function(){
    var me = this;
    
    if(this.observer){
      this.stopPolling();
    }
    
    this.observer = new IntersectionObserver(function(entries){
      if(me.destroyed) return;
      me.isIntersecting = entries[0].isIntersecting;
      me.disableHandler(!entries[0].isIntersecting);
    }, {
      threshold: 0.1,
    });
    
    if(this.getEl() && this.getEl().dom){
      this.observer.observe(this.getEl().dom);
    }
    
    if(Ext.isEmpty(this.pollingTaskId)){
      this.pollingTaskId = Ext.TaskManager.start({
        run: this.pollingTask,
        interval: this.pollingInterval,
        scope: this,
      });
    } else{
      this.pollingTask();
    }
  },
  //
  stopPolling: function(){
    if(this.pollingTaskId){
      Ext.TaskManager.stop(this.pollingTaskId);
      this.pollingTaskId = undefined;
    }
    if(this.observer && this.getEl() && this.getEl().dom){
      this.observer.unobserve(this.getEl().dom);
      this.observer.disconnect();
      this.observer = null;
    }
  },
  //
  pollingTask: function(){
    if(this.destroyed) return;
    
    let isVisible = !document.hidden, // check is user has switched to another tab browser
      isFocused = document.hasFocus(), // check is user has minimized browser window
      isIntersecting = this.isIntersecting; // switch to other application tab
    if(isIntersecting && isVisible && isFocused){ // check is user has switched to another tab or minimized browser window
      this.statusUpdate();
    }
  },
  //
  disableHandler: function(state){
    if(this.destroyed) return;
    
    var isVisible = !document.hidden, // check is user has switched to another tab browser
      isIntersecting = this.isIntersecting; // switch to other application tab
    if(this.pollingTaskId && isIntersecting && isVisible){
      this.setContainerDisabled(state);
      this.pollingTask();
    }
  },
  //
  setContainerDisabled: function(state){
    if(this.destroyed) return;
    
    let icon;
    this.navTree.setDisabled(state);
    if(state){
      icon = this.generateIcon(true, "stop-circle-o", "grey", __("suspend"));
    } else{
      icon = this.generateIcon(true, "circle", NOC.colors.yes, __("online"));
    }
    if(this.getViewModel()){
      this.getViewModel().set("icon", icon);
    }
  },
  subscribeToEvents: function(){
    this.handleWindowFocus = this.handleWindowFocus.bind(this);
    this.handleWindowBlur = this.handleWindowBlur.bind(this);
    window.addEventListener("focus", this.handleWindowFocus);
    window.addEventListener("blur", this.handleWindowBlur);
  },
  
  unsubscribeFromEvents: function(){
    if(this.handleWindowFocus){
      window.removeEventListener("focus", this.handleWindowFocus);
    }
    if(this.handleWindowBlur){
      window.removeEventListener("blur", this.handleWindowBlur);
    }
  },
  //
  destroy: function(){
    this.destroyed = true;
    
    this.unsubscribeFromEvents();
    this.stopPolling();
    this.setContainerDisabled(false);
    
    this.isRefreshing = false;
    this.isUpdating = false;
    
    this.callParent();
  },
  //
  handleWindowFocus: function(){
    if(this.destroyed) return;
    var me = this;
    setTimeout(function(){
      if(!me.destroyed){
        me.disableHandler(false);
      }
    }, 100);
  },
  //
  handleWindowBlur: function(){
    if(this.destroyed) return;
    this.disableHandler(true);
  },
  //
  statusUpdate: function(){
    if(this.destroyed || this.isUpdating) return;
    this.isUpdating = true;
    this.getViewModel().set("icon", this.generateIcon(true, "spinner", "grey", __("loading")));
    Ext.Ajax.request({
      url: "/inv/inv/resource_status/",
      method: "POST",
      jsonData: {
        resources: Ext.Array.map(this.store.getData().filterBy(function(item){return item.isVisible}).items, function(item){return `o:${item.id}`}),
      },
      scope: this,
      success: function(response){
        if(this.destroyed) return;
        let data = Ext.decode(response.responseText);
        data.resource_status.forEach(element => {
          const id = element.resource.slice(2),
            record = this.store.getById(id);
          if(!Ext.isEmpty(record)){
            record.set("is_alarm", element.is_alarm);
          }
        });
        this.navTree.getView().refresh();
      },
      failure: function(){
        if(!this.destroyed){
          NOC.error(__("Failed to update alarm"));
        }
      },
      callback: function(){
        if(!this.destroyed && this.getViewModel().get("autoReload")){
          this.getViewModel().set("icon", this.generateIcon(true, "circle", NOC.colors.yes, __("online")));
          this.isUpdating = false;
        }
      },
    });
  },
});
