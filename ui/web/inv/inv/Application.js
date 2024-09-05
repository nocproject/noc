//---------------------------------------------------------------------
// inv.inv application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
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
      listeners: {
        scope: me,
        beforeload: function(){
          if(this.navTree){
            this.navTree.mask(__("Loading..."));
          }
        },
        load: function(){
          if(this.navTree && this.navTree.isVisible()){
            this.navTree.unmask();
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
      hideHeaders: true,
      columns: [
        {
          xtype: "treecolumn", // Это обязательная колонка для отображения дерева
          dataIndex: "name",
          flex: 1,
        },
        {
          xtype: "widgetcolumn",
          width: 70,
          widget: {
            xtype: "button",
            text: "...",
            hidden: true,
            arrowVisible: false,
            hideMode: "visibility",
            style: {
              backgroundColor: "#ECECEC",
            },
            listeners: {
              afterrender: function(button){
                button.getEl().down(".x-btn-inner").setStyle("color", "black");
              },
            },
            menu: {},
          },
          onWidgetAttach: function(col, widget, record){
            var navTree = this.up("treepanel");
            
            if(navTree.getSelectionModel().isSelected(record)){
              widget.show();
            } else{
              widget.hide();
            }
            widget.setMenu({
              xtype: "menu",
              plain: true,
              items: [
                {
                  glyph: NOC.glyph.plus,
                  text: __("Add objects"),
                  disabled: !record.get("can_add"),
                  scope: me,
                  handler: me.onAddObject,
                },
                {
                  glyph: NOC.glyph.minus,
                  text: __("Remove group"),
                  scope: me,
                  disabled: !record.get("can_delete"),
                  handler: me.onRemoveGroup,
                },
                {
                  glyph: NOC.glyph.plug,
                  text: __("Create connection"),
                  scope: me,
                  disabled: false,
                  handler: me.onCreateConnection,
                },
                {
                  glyph: NOC.glyph.line_chart,
                  text: __("Open Dashboard"),
                  scope: me,
                  disabled: false,
                  handler: me.onOpenDashboard,
                },
                {
                  glyph: NOC.glyph.copy,
                  text: __("Clone"),
                  scope: me,
                  handler: me.onClone,
                },
                {
                  itemId: "invNavContextMenuMap",
                  text: __("Show Map"),
                  glyph: NOC.glyph.globe,
                  scope: me,
                  handler: me.onShowMap,
                  // arrowVisible: false,
                  disabled: true,
                  menu: [], // Dynamically add items, after select node in navigation, method 'onSelectNav'
                },
              ],
            });
          },
        },
      ],
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        items: [
          me.navReloadButton,
          "->",
          {
            glyph: NOC.glyph.plus,
            tooltip: __("Add objects"),
            itemId: "addObjectDock",
            disabled: false,
            scope: me,
            handler: me.onAddObject,
          },

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
    me.navTree.getView().on("beforedrop", me.onNavDrop, me);
    me.tabPanel = Ext.create("Ext.tab.Panel", {
      region: "center",
      layout: "fit",
      border: false,
      scrollable: true,
      defaults: {
        scrollable: true,
      },
      items: [],
      listeners: {
        scope: me,
        beforetabchange: function(tabPanel, newCard){
          var me = this,
            objectId = me.selectedObjectId,
            pluginName = newCard.pluginName;
          Ext.Ajax.request({
            url: "/inv/inv/" + objectId + "/plugin/" + pluginName + "/",
            method: "GET",
            scope: me,
            success: function(response){
              var data = Ext.decode(response.responseText);
              newCard.preview(data, objectId);
            },
            failure: function(){
              NOC.error(__("Failed to get data for plugin") + " " + pluginName);
            },
          });
        },
      },
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
  runPlugin: function(objectId, pData){
    var me = this,
      plugin = Ext.create(pData.xtype, {app: me});
    me.tabPanel.add(plugin);
    me.invPlugins[pData.name] = plugin;
    plugin.pluginName = pData.name;
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
  onSelectNav: function(rowModel, record){
    var mapMenuItem, me = this,
      objectId = record.get("id"),
      plugins = record.get("plugins"),
      vwidgetColumn = rowModel.view.getHeaderCt().down('widgetcolumn'),
      widget = vwidgetColumn.getWidget(record),
      menu = widget.getMenu();

    if(widget){
      var innerCells = widget.getEl().up(".x-grid-row");
      Ext.each(innerCells.query(".x-grid-cell-inner"), function(cell){
        cell.classList.add("noc-inv-nav-cell-inner");
      });
      me.down("#addObjectDock").hide();
      widget.show();
      mapMenuItem = widget.down("#invNavContextMenuMap");
      if(mapMenuItem){
        menu.remove(mapMenuItem);
      }
      me.selectedObjectId = objectId;
      me.tabPanel.mask(__("Loading..."));
      setTimeout(function(){
        Ext.Ajax.request({
          url: "/inv/inv/" + objectId + "/map_lookup/",
          method: "GET",
          success: function(response){
            var defaultHandler, menuItems,
              data = Ext.decode(response.responseText);

            if(Ext.isEmpty(data)){
              menu.add({
                itemId: "invNavContextMenuMap",
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
              menu.add({
                itemId: "invNavContextMenuMap",
                text: __("Show Map"),
                glyph: NOC.glyph.globe,
                menu: menuItems,
              });
            } else{
              menu.add({
                itemId: "invNavContextMenuMap",
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
        me.invPlugins = {};
        me.tabPanel.removeAll();
        Ext.each(plugins, function(p){
          me.runPlugin(objectId, p);
        });
        me.tabPanel.setActiveTab(0);
        me.setHistoryHash(objectId);
        me.tabPanel.unmask();
      }, 0);
    }
  },
  //
  onDeselect: function(rowModel, record){
    var vwidgetColumn, widget, me = this;

    me.down("#addObjectDock").show();
    if(rowModel){
      vwidgetColumn = rowModel.view.getHeaderCt().down('widgetcolumn');
      widget = vwidgetColumn.getWidget(record);
      if(widget){
        widget.hide();
      }
    }
    me.tabPanel.removeAll();
    me.setHistoryHash();
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
          if(Object.prototype.hasOwnProperty.call(data, "choices")){
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
                      loadMask: true,
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
          } else if(Object.prototype.hasOwnProperty.call(data, "status") && data.status){
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
  onRemoveGroup: function(){
    var me = this,
      sm = me.navTree.getSelectionModel(),
      sel = sm.getSelection(),
      container = null;
    if(sel.length > 0){
      container = sel[0];
    }
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
              sm.deselect(container);
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
    
    if(me.mainPanel.items.items.length > 2){
      me.mainPanel.remove(me.mainPanel.items.items[2], false);
    }
    if(selected.length > 0){
      me.mainPanel.add(me.connectionPanel);
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
        } else{
          me.store.reload({
            node: me.store.getRootNode(),
            callback: function(){
              var path = container.getPath().replace("/" + container.id, "");
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
});
