//---------------------------------------------------------------------
// core.tagfield.treepicker controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.tagfield.TreePickerController");

Ext.define("NOC.core.tagfield.TreePickerController", {
  extend: "Ext.app.ViewController",
  alias: "controller.core.tagfield.treepicker",
  requires: [],
  // store events
  onLoadTree: function(store, records, success){
    var parentNode = this.getParentNode(),
      me = this.getView(),
      parentField = me.scope;
    if(!parentNode.hasChildNodes() && success){
      parentNode.appendChild(records.map(function(item){
        return Ext.merge({
          leaf: !item.get("has_children"),
          qtip: item.get(parentField.displayField),
        }, item.getData());
      }));
      parentNode.expand();
    }
    if(!me.cache){ // first run, root elements
      me.cache = Ext.clone(parentNode.childNodes);
    }
  },
  // tree panel events
  onClosePanel: function(){
    this.getView().hide();
  },
  onItemClick: function(view, record){
    this.selectItem(record);
  },
  onPickerKeyDown: function(view, record, item, index, e){
    var key = e.getKey();
    if(key === e.ENTER){
      this.selectItem(record);
    }
  },
  onItemBeforeExpand: function(self){
    var me = this.getView(), node;
    if(me.currentLeaf && (me.currentLeaf !== self.getId())){
      node = me.getStore().getNodeById(me.currentLeaf);
      node.appendChild(me.cache);
    }
    me.currentLeaf = self.getId();
    me.cache = Ext.clone(self.childNodes);
    if(!self.hasChildNodes()){
      this.loadChildren(me.currentLeaf);
      return false;
    }
  },
  onItemExpand: function(){
    this.doFilter();
  },
  onLeaveFocusTreePicker: function(){
    this.getView().scope.setEditable(true);
    this.getView().hide();
  },
  // search field events
  onClearSearchField: function(self){
    self.setValue();
    self.getTrigger("clear").hide();
    this.doFilter();
  },
  onChangeSearchField: function(self){
    if(self.getValue() == null || !self.getValue().length){
      this.onClearSearchField(self);
      return;
    }
    this.doFilter();
    self.getTrigger("clear").show();
  },
  //
  getParentNode: function(){
    var me = this.getView(), store = me.getStore();
    if(!me.currentLeaf){
      return store.getRootNode();
    } else{
      return store.getById(me.currentLeaf);
    }
  },
  loadChildren: function(id){
    var me = this.getView();
    if(!me.hidden){
      me.mask(__("loading ..."));
    }
    me.treeStore.load({
      params: {
        parent: id,
      },
      callback: function(){
        if(!me.hidden){
          me.unmask();
        }
      },
    });
  },
  selectItem: function(record){
    var parent = this.getView().scope, value = {}, isExist,
      selected = parent.getSelected();
    if(selected){
      isExist = Ext.Array.findBy(selected, function(el){
        return el.id === record.id
      });
    }
    if(isExist){
      parent.removeValue(isExist);
    } else{
      value[parent.valueField] = record.id;
      value[parent.displayField] = record.get(parent.displayField);
      parent.addValue(Ext.create("Ext.data.Model", value));
    }
  },
  selectNode: function(){
    var me = this.getView(), selection = [];
    if(me){
      // maping to tree-picker store
      Ext.Array.each(me.scope.getPicker().getSelectionModel().getSelection(), function(record){
        var node = me.getStore().getNodeById(record.id);
        if(node){
          selection.push(node);
        }
      });
      if(selection.length){
        me.getSelectionModel().select(selection);
      }
      if(selection.length === 0){
        me.getSelectionModel().deselectAll(selection);
      }
    }
  },
  doFilter: function(){
    var me = this.getView(), parentNode = this.getParentNode(),
      searchField = me.down("[xtype=searchfield]");
    if(parentNode){
      me.getStore().filterBy(function(record){
        if(record.parentNode.id !== me.currentLeaf){
          return true;
        }
        if(!searchField.getValue()){
          return true;
        }
        return record.get(me.scope.displayField).toLowerCase().indexOf(searchField.getValue().toLowerCase()) !== -1;
      })
      this.selectNode();
    }
  },
});
