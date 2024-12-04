//---------------------------------------------------------------------
// NOC.core.TreePanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.TreePanel");

Ext.define("NOC.core.TreePanel", {
  extend: "Ext.panel.Panel",

  requires: [
    "Ext.ux.form.SearchField",
  ],

  alias: "widget.nocTreePanel",

  currentId: "",
  generator: undefined,
  queryPrevLength: 0,
  itemId: "treePanel",
  resizable: false,
  iconWidth: 21,

  action: function(){
    console.error("You must declare action on item click!")
  },

  initComponent: function(){
    var me = this,
      clickFn = function(element, td, cellIndex, record, tr, rowIndex){
        if(record.get("generator")){
          me.generator = record.get("generator");
        }
        if("history" === element.grid.itemId){
          if(me.actionAlways && cellIndex && cellIndex === 1){
            me._action(me, record, true);
            me.byIdQuery(record.data.id, true);
          } else{
            var maxIndex = me.historyStore.getCount();
            for(var i = rowIndex + 1; i < maxIndex; i++){
              me.historyStore.remove(me.historyStore.last());
            }
            me.byIdQuery(record.data.id, false);
          }
        } else{
          if(hasChild(record.data)){
            if(me.actionAlways && cellIndex && cellIndex === 2){
              me._action(me, record, true);
              me.byIdQuery(record.data.id, true);
            } else{
              record.data.level = me.historyStore.max("level") + 1;
              me.historyStore.add(record.data);
              me.byIdQuery(record.data.id, false);
            }
          } else{
            me._action(me, record, false);
          }
        }
      },
      hasChild = function(node){
        return "has_children" in node && node.has_children;
      },
      isOpen = function(node){
        return me.pathStore.contains(node);
      };

    this.searchField = Ext.create("Ext.ux.form.SearchField", {
      store: this.listStore,
      xtype: "searchfield",
      itemId: "filter",
      width: "95%",
      emptyText: __("pattern"),
      flex: 1,

      enableKeyEvents: true,
      triggers: {
        clear: {
          cls: "x-form-clear-trigger",
          scope: me,
          hidden: true,
          handler: Ext.pass(this.onClearFilter, true),
        },
      },
      listeners: {
        scope: this,
        keyup: this.filterListener,
      },
    });

    this.history = Ext.create("Ext.grid.Panel", {
      itemId: "history",
      hideHeaders: true,
      disableSelection: true,
      tbar: [
        this.searchField,
        {
          xtype: "button",
          handler: me.closeSelectWindow,
          glyph: 0xf00d,
        },
      ],
      columns: [
        {
          dataIndex: "label",
          flex: 1,
          renderer: function(value, metadata, record){
            return '<i class="fa fa-folder-open-o" aria-hidden="true" style="padding-left: '
                            + 6 * record.data.level + 'px"></i><b style="padding-left: 6px">'
                            + value + "</b>";
          },
        }, {
          width: this.iconWidth,
          renderer: function(){
            return '<i class="fa fa-location-arrow" aria-hidden="true"></i>';
          },
        },
      ],
      store: this.historyStore,
      listeners: {
        cellclick: clickFn,
      },
    });

    this.list = Ext.create("Ext.grid.Panel", {
      itemId: "list",
      hideHeaders: true,
      disableSelection: false,
      border: false,
      selModel: {
        mode: "SINGLE",
        selType: "checkboxmodel",
        showHeaderCheckbox: false,
      },
      emptyText: __("empty list"),
      store: this.listStore,
      columns: [{
        dataIndex: "label",
        flex: 1,
        renderer: function(value, metadata, record){
          var icon,
            padding = 6;
          if(hasChild(record.data)){
            icon = '<i class="fa fa-folder-o" aria-hidden="true"></i>';
            if(isOpen(record)){
              icon = '<i class="fa fa-folder-open-o" aria-hidden="true"></i>';
            }
          } else{
            padding = 16;
          }
          return Ext.String.format('{0}<span style="padding-left: {1}px" title="{2}">{2}</span>', icon, padding, value);
        },
      }, {
        width: this.iconWidth,
        renderer: function(value, metadata, record){
          if(hasChild(record.data)){
            return '<i class="fa fa-location-arrow" aria-hidden="true"></i>';
          } else{
            return "";
          }
        },
      }],
      listeners: {
        scope: this,
        cellclick: clickFn,
        select: function(rowModel, record){
          this.listStore.suspendEvents();
          this.listStore.remove(record);
          this.listStore.insert(0, record);
          this.listStore.resumeEvents();
          this.listStore.fireEvent("datachanged", this.listStore);
          this.list.getSelectionModel().select(0);
        },
      },
    });

    Ext.apply(me, {
      items: [
        this.history,
        this.list,
      ],
    });

    this.callParent(arguments);
  },

  // --- Load data ---
  loadList: function(params){
    if(this.generator){
      Ext.apply(params, {generator: this.generator});
    }
    this.listStore.load({
      scope: this,
      params: params,
      callback: this.selectListRow,
    });
  },

  selectListRow: function(){
    var allSelected = this.pathStore.getData().getRange().concat(this.fieldValue());

    Ext.Array.each(allSelected, function(item){
      var indexRow = this.listStore.indexOf(item);
      if(indexRow >= 0){
        this.list.getSelectionModel().select(indexRow);
        return true;
      }
      this.list.getSelectionModel().deselectAll();
    }, this);
  },

  byIdQuery: function(id, isClosePanel, generator){
    if("_root_" === id){
      id = "";
    }
    if(isClosePanel){
      this.closeSelectWindow();
    }
    if(generator){
      this.generator = generator
    }
    this.loadList({parent: id});
    this.currentId = id;
    this.onClearFilter(false);
  },

  filterQuery: function(value){
    var extraParams = {parent: this.currentId};
    if(value.length > 0){
      Ext.apply(extraParams, {
        __query: value,
        __format: "ext",
      });
    }
    this.loadList(extraParams);
    this.queryPrevLength = value.length;
  },

  filterListener: function(field, event){
    var value = field.getValue();

    if(value.length === 0){
      this.searchField.getTrigger("clear").hide();
      this.filterQuery(value);
      return;
    }
    if(Ext.EventObject.ENTER === event.getKey()){
      this.filterQuery(value);
    } else{
      if(Math.abs(this.queryPrevLength - value.length) >= 2){
        this.filterQuery(value);
      }
    }
    this.searchField.getTrigger("clear").show();
  },

  _action: function(me, record, hasChild){
    me.action(record, hasChild);
    me.pathStore.removeAll();
    me.pathStore.add(Ext.Array.map(me.historyStore.getRange(), function(record){
      return record.copy();
    }));
    me.fieldValue(record);
    me.list.getView().refresh();
  },

  onClearFilter: function(withQuery){
    this.searchField.setValue("");
    this.searchField.getTrigger("clear").hide();
    if(withQuery){
      this.filterQuery("");
    }
  },
});
