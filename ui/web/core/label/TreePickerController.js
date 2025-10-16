//---------------------------------------------------------------------
// core.label.treepicker controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.label.TreePickerController");

Ext.define("NOC.core.label.TreePickerController", {
  extend: "Ext.app.ViewController",
  alias: "controller.core.label.treepicker",
  requires: [
    "NOC.core.label.LabelFieldModel",
  ],
  // tree panel events
  onClosePanel: function(){
    this.getView().fireEvent("closeTreePicker");
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
  onLeaveFocusTreePicker: function(){
    this.getView().scope.setEditable(true);
    this.getView().fireEvent("closeTreePicker");
  },
  selectItem: function(record){
    if(!record.get("leaf")){
      return;
    }
    var parent = this.getView().scope, value = {}, isExist, pattern,
      selected = parent.getValue();
    if(selected){
      pattern = record.id.toLowerCase();
      isExist = Ext.Array.findBy(selected, function(el){
        return el.toLowerCase() === pattern;
      });
    }
    if(isExist){
      parent.removeValue(isExist);
    } else{
      // value = Ext.create("NOC.core.label.LabelFieldModel", {
      //     id: record.id,
      //     name: record.get("name"),
      //     scope: record.get("scope"),
      //     value: record.get("value"),
      //     is_protected: record.get("is_protected"),
      //     bg_color1: record.get("bg_color1"),
      //     bg_color2: record.get("bg_color2"),
      //     fg_color1: record.get("fg_color1"),
      //     fg_color2: record.get("fg_color2"),
      // });
      value = {
        id: record.id,
        name: record.get("name"),
        scope: record.get("scope"),
        value: record.get("value"),
        is_protected: record.get("is_protected"),
        bg_color1: record.get("bg_color1"),
        bg_color2: record.get("bg_color2"),
        fg_color1: record.get("fg_color1"),
        fg_color2: record.get("fg_color2"),
      };
      parent.addValue(Ext.create("NOC.core.label.LabelFieldModel", value));
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
  doFilter: function(){
    var me = this.getView(),
      isContains = function(record, value){
        return record.get(me.scope.displayField).toLowerCase().indexOf(value.toLowerCase()) !== -1;
      },
      checkChild = function(record){
        if(record.childNodes.length){
          var ret = false;
          for(var i = 0; i < record.childNodes.length; i++){
            if(isContains(record.childNodes[i], searchField.getValue())){
              ret = true;
              break;
            }
            if(record.childNodes[i].childNodes.length) checkChild(record.childNodes[i]);
          }
          if(ret) return true;
        }
      },
      searchField = me.dockedItems.items[1].down("[xtype=searchfield]");
    me.getStore().filterBy(function(record){
      if(!searchField.getValue()){
        return true;
      }
      if(checkChild(record, searchField.getValue())) return true;
      return isContains(record, searchField.getValue())
    })
    this.selectNode();
  },
});
