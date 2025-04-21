//---------------------------------------------------------------------
// sa.managedobject ConfDBPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.ConfDBPanel");

Ext.define("NOC.sa.managedobject.ConfDBPanel", {
  extend: "NOC.core.ApplicationPanel",
  app: null,
  alias: "widget.sa.confdb",
  requires: [
    "NOC.core.ComboBox",
    "NOC.core.CodeViewer",
  ],
  layout: "border",
  //
  initComponent: function(){
    var me = this;

    me.currentObject = null;
    me.defaultRoot = {
      text: __("."),
      expanded: true,
      children: [],
    };
    me.store = Ext.create("Ext.data.TreeStore", {
      root: me.defaultRoot,
      listeners: {
        scope: me,
        endupdate: this.leafCount,
      },
    });
    me.searchField = Ext.create({
      xtype: "textfield",
      emptyText: __("Search ..."),
      flex: 2,
      enableKeyEvents: true,
      anchor: "100%",
      triggers: {
        clear: {
          cls: "x-form-clear-trigger",
          hidden: true,
          weight: -1,
          handler: function(field){
            field.setValue(null);
            field.fireEvent("select", field);
          },
        },
      },
      listeners: {
        change: function(field, value){
          if(value == null || value === ""){
            field.getTrigger("clear").hide();
            this.clearFilter();
            return;
          }
          field.getTrigger("clear").show();
        },
        scope: me,
        specialkey: me.onSpecialKey,
      },
    });
    me.matchField = Ext.create({
      xtype: "displayfield",
    });
    // Buttons
    me.refreshButton = Ext.create("Ext.button.Button", {
      text: __("Refresh"),
      glyph: NOC.glyph.refresh,
      scope: me,
      handler: me.onRefresh,
    });
    me.queryButton = Ext.create("Ext.button.Button", {
      text: __("Query"),
      glyph: NOC.glyph.search_plus,
      enableToggle: true,
      scope: me,
      handler: me.onToggleQueryPanel,
    });
    me.cleanupButton = Ext.create({
      xtype: "checkbox",
      boxLabel: __("Cleanup"),
      scope: me,
      checked: true,
      handler: me.onRefresh,
    });
    me.runButton = Ext.create("Ext.button.Button", {
      text: __("Run"),
      glyph: NOC.glyph.play,
      disabled: true,
      scope: me,
      handler: me.runQuery,
    });
    me.closeQueryButton = Ext.create("Ext.button.Button", {
      tooltip: __("Close Query"),
      glyph: NOC.glyph.times,
      scope: me,
      handler: me.onCloseQuery,
    });
    me.helpButton = Ext.create("Ext.button.Button", {
      tooltip: __("Help"),
      glyph: NOC.glyph.question,
      scope: me,
      handler: me.onHelp,
    });
    // Panels
    me.confDBTree = Ext.create({
      xtype: "treepanel",
      store: me.store,
      rootVisible: false,
      useArrows: true,
    });

    me.confDBPanel = Ext.create({
      xtype: "panel",
      region: "center",
      layout: "fit",
      width: "70%",
      scrollable: true,
      tbar: [
        me.getCloseButton(),
        me.refreshButton,
        me.queryButton,
        "-",
        me.cleanupButton,
        "->",
        me.searchField,
        me.matchField,
      ],
      items: [
        me.confDBTree,
      ],
    });
    
    me.queryField = Ext.create("NOC.core.CodeViewer", {
      value: "",
      language: "python",
      readOnly: false,
      theme: "vs-dark",
      automaticLayout: true,
      contentChanged: function(viewer, value){
        me.runButton.setDisabled(!value);
      },
    });
      
    me.confDBQueryField = Ext.create({
      xtype: "core.combo",
      restUrl: "/cm/confdbquery/lookup/",
      uiStyle: "medium-combo",
      listeners: {
        scope: me,
        change: function(field, value){
          if(Ext.isEmpty(value)) return
          Ext.Ajax.request({
            url: "/cm/confdbquery/" + value + "/",
            scope: me,
            success: function(response){
              var data = Ext.decode(response.responseText);
              me.queryField.setValue(data.source);
            },
            failure: function(){
              NOC.error(__("Failed to load data"));
            },
          })
        },
      },
    });

    me.queryPanel = Ext.create({
      xtype: "panel",
      region: "center",
      height: "30%",
      layout: "fit",
      items: [
        me.queryField,
      ],
      tbar: [
        me.runButton,
        me.closeQueryButton,
        me.confDBQueryField,
        "->",
        me.helpButton,
      ],
    });
    me.resultPanel = me.createResultPanel();
    me.rightPanel = Ext.create({
      xtype: "panel",
      layout: "border",
      region: "east",
      width: "30%",
      split: true,
      hidden: true,
      stateful: true,
      stateId: "sa.confdb.right",
      items: [
        me.queryPanel,
        me.resultPanel,
      ],

    });
    Ext.apply(me, {
      layout: "border",
      items: [
        me.confDBPanel,
        me.rightPanel,
      ],
    });
    me.callParent();
  },
  //
  setConfDB: function(data){
    var me = this,
      result = {
        text: ".",
        expanded: true,
        children: [],
      },
      applyNode = function(node, conf){
        Ext.each(conf, function(item){
          var r = {
            text: item.node,
          };
          if(item.children){
            r.children = [];
            applyNode(r, item.children);
            r.expanded = r.children.length < 100
          } else{
            r.leaf = true
          }
          node.children.push(r)
        })
      };
    me.store.removeAll();
    applyNode(result, data);
    me.store.setRootNode(result);
  },
  //
  preview: function(record){
    var me = this;
    me.callParent(arguments);
    me.setTitle(record.get("name") + " ConfDB");
    me.confDBTree.mask();
    me.url = "/sa/managedobject/" + record.get("id") + "/confdb/";
    Ext.Ajax.request({
      url: me.url + "?cleanup=" + me.cleanupButton.value,
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        me.setConfDB(data);
        me.confDBTree.unmask()
      },
      failure: function(){
        NOC.error(__("Failed to load data"));
        me.confDBPTree.unmask()
      },
    });
  },
  //
  onRefresh: function(){
    var me = this;
    if(me.queryButton.pressed){
      me.runQuery();
    } else{
      me.preview(me.currentRecord);
    }
  },
  //
  onSpecialKey: function(field, key){
    var me = this;
    if(field.xtype !== "textfield")
      return;
    switch(key.getKey()){
      case Ext.EventObject.ENTER:
        key.stopEvent();
        me.setFilter(field.getValue());
        break;
      case Ext.EventObject.ESC:
        key.stopEvent();
        field.setValue(null);
        break;
    }
  },
  //
  setFilter: function(value){
    var me = this, matches = 0, searchPattern;
    try{
      searchPattern = new RegExp(value, "i");
      Ext.suspendLayouts();
      me.store.filter({
        filterFn: function(node){
          var children = node.childNodes,
            len = children && children.length,
            visible = node.isLeaf() ? searchPattern.test(node.get("text")) : false,
            i;

          for(i = 0; i < len && !(visible = children[i].get("visible")); i++);

          if(visible && node.isLeaf()){
            matches++;
          }
          return visible;
        },
      });
      me.setMatched(matches);
      Ext.resumeLayouts(true);
    } catch(e){
      console.error(e);
      NOC.error(__("Invalid regular expression"));
    }
  },
  //
  clearFilter: function(){
    var me = this;
    me.store.clearFilter();
    me.leafCount();
  },
  //
  onToggleQueryPanel: function(){
    var me = this;
    if(me.rightPanel.isHidden()){
      me.rightPanel.show();
    } else{
      me.rightPanel.hide();
    }
  },
  //
  onHelp: function(){
    console.log("show help, not implemented");
  },
  //
  onCloseQuery: function(){
    var me = this;
    me.queryButton.setPressed(false);
    me.onToggleQueryPanel();
  },
  //
  leafCount: function(){
    var me = this, leafCount = 0;
    if(me.store){
      me.store.getRoot().visitPostOrder("", function(node){
        if(node.isLeaf()){
          leafCount++;
        }
      });
      me.setMatched(leafCount);
    }
  },
  //
  runQuery: function(){
    var me = this, query = {dump: true};
    me.mask(__("Querying ..."));
    query["cleanup"] = me.cleanupButton.value;
    query["query"] = Ext.String.trim(
      me.queryField.getValue(),
    );
    Ext.Ajax.request({
      url: me.url,
      method: "POST",
      scope: me,
      jsonData: query,
      success: function(response){
        var result,
          data = Ext.decode(response.responseText);
        if(data.status){
          me.resultPanel.destroy();
          result = data.result.map(function(element){
            if(Ext.Object.isEmpty(element)){
              return {result: "Empty Context"};
            }
            return element;
          });
          me.rightPanel.add(me.resultPanel = this.createResultPanel(result));
          me.setConfDB(data.confdb);
        } else{
          NOC.error(data.error);
        }
      },
      failure: function(){
        NOC.error(__("Query failure"))
      },
      callback: function(){
        me.unmask();
      },
    });
  },
  //
  setMatched: function(count){
    var me = this;
    me.matchField.setValue(__("Matched") + ":&nbsp;" + count);
  },
  //
  createResultPanel: function(data){
    var keys = {},
      cols = [],
      conf = {
        xtype: "panel",
        region: "south",
        height: "70%",
        split: true,
        stateful: true,
        stateId: "sa.confdb.query",
      };
    if(data){
      Ext.each(data, function(e){
        Ext.each(Object.keys(e), function(k){
          keys[k] = true;
        })
      });
      Ext.each(Object.keys(keys), function(e){
        cols.push({text: e, dataIndex: e})
      });
      Ext.merge(conf, {
        xtype: "grid",
        scrollable: true,
        columns: cols,
        store: {
          fields: keys,
          data: data,
        },
        emptyText: __("No data found"),
        tbar: [
          {
            xtype: "displayfield",
            value: __("Result"),
          },
          "->",
          {
            xtype: "displayfield",
            value: __("Total") + ":&nbsp;" + data.length,
          }],
      });
    }
    return Ext.create(conf);
  },
});
