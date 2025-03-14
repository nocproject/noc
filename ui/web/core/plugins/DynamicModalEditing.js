//---------------------------------------------------------------------
// NOC.core.plugins DynamicModalEditing for grid cell editing
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.plugins.DynamicModalEditing");

Ext.define("NOC.core.plugins.DynamicModalEditing", {
  extend: "Ext.AbstractPlugin",
  alias: "plugin.dynamicmodalediting",
  requires: [
    "Ext.window.Window",
    "Ext.form.Panel",
  ],
  init: function(grid){
    this.grid = grid;        
    grid.on("cellclick", function(view, cell, cellIndex, record){
      var column = grid.getColumnManager().getHeaderAtIndex(cellIndex);
      if(column && column.useModalEditor){
        this.showEditor(record, column, view, cell);
      }
    }, this);
  },
    
  showEditor: function(record, column){
    var dataIndex = column.dataIndex,
      formType = this.getFormType(record);
    
    if(Ext.isEmpty(formType)) return;
        
    var formItems = this.getFormItems(record, formType);
    if(!formItems || formItems.length === 0) return;
    
    this.record = record;
    this.formType = formType;
    this.formPanel = Ext.create("Ext.form.Panel", {
      bodyPadding: 10,
      border: false,
      layout: "anchor",
      scrollable: true,
      defaults: {
        anchor: "100%",
      },
      items: formItems,
    });
        
    Ext.create("Ext.window.Window", {
      title: __("Edit value"),
      modal: true,
      width: this.getEditorWidth(),
      height: this.getEditorHeight(),
      layout: "fit",
      autoShow: true,
      items: this.formPanel,
      buttons: [{
        text: __("Cancel"),
        handler: function(){
          this.up("window").close();
        },
      }, {
        text: __("Reset"),
        scope: this,
        handler: this.resetForm,
      }, {
        text: __("Save"),
        scope: this,
        handler: function(button){
          var values = this.formPanel.getForm().getValues(),
            result = this.formatResult(values);
          record.set(dataIndex, result);
          this.request("/sa/managed_object/<id>/capabilities/<caps_id>/", result, button.up("window").close);
        },
      }],
    });
  },
  
  request: function(url, data, success){
    Ext.Ajax.request({
      url: url,
      method: "PUT",
      jsonData: data,
      success: function(response){
        var result = Ext.decode(response.responseText);
        success();
      },
      failure: function(response){
        var error = Ext.decode(response.responseText);
      },
    });
  },
  getFormType: function(record){
    if(Ext.isEmpty(record.get("editor"))){
      return;
    }
    if(!Ext.isEmpty(record.get("editor"))){
      return record.get("editor").type;
    }
    return "str";
  },
    
  getFormItems: function(record, formType){
    var value = record.get("value"),
      isMultiple = record.get("editor").multiple || false;
    
    if(isMultiple){
      var values = Ext.isArray(value) ? value : [value],
        rows = [];
      if(values.length === 0){
        return [this.getMultiRowConfig(record, formType, values[0], true)];
      }
      Ext.Array.each(values, function(val, index, array){
        var isLast = index === array.length - 1;
        rows.push(this.getMultiRowConfig(record, formType, val, isLast));
      }, this);
      return rows;
    }
    return [this.getDefaultField(formType, value, record.get("editor").choices)];
  },
    
  getDefaultField: function(formType, value, choices){
    var dataIndex = "value",
      field = {
        fieldLabel: __("Value"),
        name: dataIndex,          
      };
    switch(formType){
      case "bool":
        return Ext.apply(field, {
          xtype: "checkboxfield",
          checked: value === true,
        });
      case "int":
      case "float":
        return Ext.apply(field, {
          xtype: "numberfield",
          value: value,
        });
      case "choices":
        return Ext.apply(field, {
          xtype: "combobox",
          editable: false,
          queryMode: "local",
          value: value,
          store: choices,
        });
      default:
        return Ext.apply(field, {
          xtype: "textfield",
          value: value,
        });
    }
  },
    
  getEditorWidth: function(){
    return 400;
  },
    
  getEditorHeight: function(){
    return 250;
  },
  
  getMultiRowConfig: function(record, formType, value, isLast){
    var formField = this.getDefaultField(formType, value, record.get("editor").choices),
      formWidth = this.getEditorWidth();
      
    formField.width = formWidth - 80;
    delete formField.fieldLabel;
    return {
      xtype: "container",
      layout: {
        type: "hbox",
        align: "end",
      },
      items: [
        this.getButtonConfig(isLast ? "add" : "remove"),
        formField,
      ],
    };
  },

  getButtonConfig: function(type){
    var tooltip = type === "add" ? __("Add Mapping") : __("Remove Mapping"),
      glyph = type === "add" ? NOC.glyph.plus : NOC.glyph.minus,
      config = {
        xtype: "button",
        glyph: glyph,
        tooltip: tooltip,
        disabled: false,
        scope: this,
      };
      
    if(type === "add"){
      config.handler = this.addRowButtonHandler;
    } else{
      config.handler = this.removeRow;
    }
    return config;
  },

  addRowButtonHandler: function(button){
    var newRow = this.getMultiRowConfig(this.record, this.formType, undefined, true),
      scroller = this.formPanel.getScrollable();      
      
    button.setGlyph(NOC.glyph.minus);
    button.setTooltip(__("Remove Mapping"));
    button.setHandler(this.removeRow);
    
    this.formPanel.suspendLayouts();
    this.formPanel.autoScroll = false;
    this.formPanel.add(newRow);
  
    Ext.defer(function(){
      this.formPanel.resumeLayouts(true);
      this.formPanel.autoScroll = true;
      if(scroller){
        scroller.scrollBy(0, this.formPanel.body ? this.formPanel.body.getHeight() : 10000); 
      }
    }, 100, this);
  },

  removeRow: function(button){
    var row = button.up(),
      scroller = this.formPanel.getScrollable(),
      formEl = this.formPanel.getEl(),
      scrollTop = formEl ? formEl.dom.scrollTop : 0;
    this.formPanel.suspendLayouts();
    this.formPanel.autoScroll = false;
    this.formPanel.remove(row);
    Ext.defer(function(){
      this.formPanel.resumeLayouts(true);
      this.formPanel.autoScroll = true;
      if(formEl && formEl.dom){
        scroller.scrollBy(0, scrollTop);
      }
    }, 100, this);
  },

  resetForm: function(){
    this.formPanel.removeAll();
    this.record.set("value", "");
    this.formPanel.add(this.getFormItems(this.record, this.formType));
  },

  formatResult: function(values){
    if(!Ext.isDefined(values.value)) return "-";
      
    if(Ext.isArray(values.value)){
      return Ext.Array.filter(values.value, function(val){ return !Ext.isEmpty(val); });
    }
    return values.value;
  },
});