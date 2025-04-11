//---------------------------------------------------------------------
// NOC.core.plugins SubscriptionModalEditing for grid cell editing
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.plugins.SubscriptionModalEditing");

Ext.define("NOC.core.plugins.SubscriptionModalEditing", {
  extend: "Ext.AbstractPlugin",
  alias: "plugin.subscriptionmodalediting",
  requires: [
    "NOC.core.ComboBox",
    "Ext.window.Window",
    "Ext.form.Panel",
  ],
  dataIndexes: ["crm_users", "users"], // Field names to edit
  //
  init: function(grid){
    this.grid = grid;
    grid.on("beforecellclick", function(view, cell, cellIndex, record, tr, rowIndex, e){
      var column = e.position.column;
      this.appId = view.up("[appId]").appId;
      this.objectId = view.up("[appId]").currentRecordId;
      if(column && this.dataIndexes.includes(column.dataIndex)){
        if(column.dataIndex === "users"){
          this.titleSuffix = __("Users");
        }
        if(column.dataIndex === "crm_users"){
          this.titleSuffix = __("CRM Users");
        }
        this.dataIndex = column.dataIndex;
        this.lookupUrl = column.lookupUrl || "lookUrl_not_set";
        this.showEditor(record, column, view, cell);
        return false; // Prevent default cell click action
      }
      return true;
    }, this);
  },
  //
  showEditor: function(record){
    var formItems = this.getFormItems(record),
      title = __("Group") + ": "
        + record.get("notification_group__label")
        + " " + (Ext.isEmpty(this.titleSuffix) ? "" : this.titleSuffix);
    if(!record.get("allow_edit")) return;
    this.record = record;
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
      title: title,
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
          this.request("POST", button);
        },
      }],
    });
  },
  //
  getFormItems: function(record){
    var rows = [],
      value = record.get(this.dataIndex),
      values = Ext.isArray(value) ? value : [value];
    if(values.length === 0){
      return [this.getMultiRowConfig(values[0], true)];
    }
    Ext.Array.each(values, function(val, index, array){
      var isLast = index === array.length - 1;
      rows.push(this.getMultiRowConfig(val, isLast));
    }, this);
    return rows;

  },
  //
  getMultiRowConfig: function(value, isLast){
    var formField = {
        name: this.dataIndex,
        xtype: "core.combo",
        restUrl: this.lookupUrl, 
        typeAhead: false,
        editable: false,
        value: Ext.isEmpty(value) ? undefined : value.user,
        width: this.getEditorWidth() - 180,
        hideTriggerUpdate: true,
        hideTriggerCreate: true,
      },
      suppressField = {
        name: "suppress",
        xtype: "checkbox",
        margin: "0 0 0 10",
        boxLabel: __("Suppress"),
        checked: Ext.isEmpty(value) ? false : value.suppress,
      };
      
    return {
      xtype: "container",
      layout: {
        type: "hbox",
        align: "end",
      },
      items: [
        this.getButtonConfig(isLast ? "add" : "remove"),
        formField,
        suppressField,
      ],
    };
  },
  //
  addRowButtonHandler: function(button){
    var newRow = this.getMultiRowConfig(undefined, true),
      scroller = this.formPanel.getScrollable();      
      
    button.setGlyph(NOC.glyph.minus);
    button.setTooltip(__("Remove User"));
    button.setHandler(this.removeRowHandler);
    
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
  //
  removeRowHandler: function(button){
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
  //
  getEditorWidth: function(){
    return 450;
  },
  //
  getEditorHeight: function(){
    return 250;
  },
  //
  getButtonConfig: function(type){
    var tooltip = type === "add" ? __("Add User") : __("Remove User"),
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
      config.handler = this.removeRowHandler;
    }
    return config;
  },
  //
  resetForm: function(){
    Ext.Msg.show({
      title: __("Confirm Reset"),
      message: __("Are you sure you want to reset all values?"),
      buttons: Ext.Msg.YESNO,
      icon: Ext.Msg.QUESTION,
      scope: this,
      fn: function(btn){
        if(btn === "yes"){
          this.formPanel.removeAll();
          this.record.set(this.dataIndex, []);
          this.record.commit();
          this.formPanel.add(this.getFormItems(this.record));
        }
      },
    });
  },
  //
  request: function(method, button){
    var url = this.makeUrl(this.appId, this.objectId, this.record.get("notification_group")),
      data = this.getValues();
    Ext.Ajax.request({
      url: url,
      method: method,
      scope: this,
      jsonData: {[this.dataIndex]: data},
      success: function(response){
        var result = Ext.decode(response.responseText);
        if(result.success){
          this.record.set(result.data);
          this.record.commit();
          button.up("window").close();
          NOC.info(__("Subscription updated successfully"));
        } else{
          NOC.error(__("Error") + ": " + (result.message || __("Failed to update subscription")));
        }
      },
      failure: function(response){
        var result = Ext.decode(response.responseText);
        NOC.error(__("Error") + ": " + (result.errors || __("Server error occurred")));
      },
    });
  },
  //
  makeUrl: function(appId, objectId, groupId){ 
    var prefix = appId.replace(/\./g, "/");
    return Ext.String.format("/{0}/{1}/object_subscription/{2}/update/", prefix, objectId, groupId);
  },
  //
  getValues: function(){
    var values = [],
      combos = this.formPanel.query("core\\.combo[name=" + this.dataIndex + "]"),
      checkboxes = this.formPanel.query("checkbox[name=suppress]");
    Ext.Array.each(combos, function(combo, index){
      values.push({
        user: combo.getValue(),
        suppress: checkboxes[index].getValue(),
      });
    });
    return Ext.Array.filter(values, function(value){
      return !Ext.isEmpty(value.user); 
    });
  },
});