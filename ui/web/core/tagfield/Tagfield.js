//---------------------------------------------------------------------
// core.tagfield widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.tagfield.Tagfield");

Ext.define("NOC.core.tagfield.Tagfield", {
  extend: "Ext.form.field.Tag",
  alias: "widget.core.tagfield",
  controller: "core.tagfield",
  requires: [
    "NOC.core.tagfield.TagfieldController",
    "NOC.core.tagfield.TreePicker",
  ],
  displayField: "label",
  valueField: "id",
  queryMode: "remote",
  queryParam: "__query",
  queryCaching: false,
  queryDelay: 200,
  minChars: 2,
  pageSize: true,
  lazyLoadTree: false,
  pickerPosition: "left", // right | left
  store: {
    fields: ["id", "label"],
    pageSize: 25,
    proxy: {
      type: "rest",
      pageParam: "__page",
      startParam: "__start",
      limitParam: "__limit",
      sortParam: "__sort",
      extraParams: {
        "__format": "ext",
      },
      reader: {
        type: "json",
        rootProperty: "data",
        totalProperty: "total",
        successProperty: "success",
      },
    },
  },
  config: {
    selected: null,
  },
  twoWayBindable: [
    "selected",
  ],
  listeners: {
    change: "onChangeTagValue",
  },
  tipTpl: [
    "{label}",
  ],
  initComponent: function(){
    this.store.proxy.url = this.url;
    if(Ext.isFunction(this.url)){
      this.store.proxy.url = this.url();
    }
    if(this.lazyLoadTree){
      this.triggers.picker.cls = "theme-classic fas fa fa-folder-open-o";
      this.treePicker = Ext.create({
        xtype: "core.tagfield.treepicker",
        displayField: this.displayField,
        scope: this,
      });
    }
    // Fix combobox when use remote paging
    this.pickerId = this.getId() + "-picker";
    this.callParent();
  },
  setValue: function(value, add){
    var me = this;
    if(Ext.isArray(value) && value.length > 0){
      if(!Ext.isObject(value[0])){
        var params = value.map(function(element){
          var obj = {};
          obj[me.valueField] = element;
          return Ext.Object.toQueryString(obj);
        }).join("&");

        value = value.map(function(element){
          var obj = {};
          obj[me.valueField] = element;
          return obj;
        });
        Ext.Ajax.request({
          url: me.store.proxy.url,
          method: "GET",
          scope: me,
          params: params,
          success: function(response){
            me.setValue(Ext.decode(response.responseText));
          },
        });
      } else{
        me.store.loadData(value);
      }
    }
    return me.callParent([value.map(function(element){
      return element[me.valueField];
    }), add]);
  },
  setSelected: function(value, skip){
    this.callParent([value]);
    if(!skip){
      this.setWidgetValues(value);
    }
  },
  setWidgetValues: function(data){
    this.setSelection(data);
  },
  onTriggerClick: function(el){
    if(!el){
      return;
    }
    if(this.lazyLoadTree){
      var position,
        heightAbove = this.getPosition()[1] - Ext.getBody().getScroll().top,
        heightBelow = Ext.Element.getViewportHeight() - heightAbove - this.getHeight();
      this.treePicker.setWidth(this.getWidth());
      this.treePicker.height = Math.max(heightAbove, heightBelow) - 5;
      this.setEditable(false);
      position = this.getPosition();
      if(this.pickerPosition === "left"){
        position[0] = position[0] - this.getWidth();
      } else if(this.pickerPosition === "right"){
        position[0] = position[0] + this.getWidth();
      }
      if(heightAbove > heightBelow){
        position[1] -= this.treePicker.height - this.getHeight();
      }
      this.treePicker.showAt(position);
    } else{
      Ext.form.field.Tag.prototype.onTriggerClick.apply(this, arguments);
    }
  },
});
