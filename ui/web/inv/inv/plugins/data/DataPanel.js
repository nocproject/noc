//---------------------------------------------------------------------
// inv.inv LAG Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.data.DataPanel");

Ext.define("NOC.inv.inv.plugins.data.DataPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.data.DataModel",
  ],
  title: __("Data"),
  closable: false,
  layout: "fit",

  initComponent: function(){
    var me = this;

    // Data Store
    me.store = Ext.create("Ext.data.Store", {
      // model: "NOC.inv.inv.plugins.data.DataModel",
      groupField: "interface",
    });
    // Grids
    Ext.apply(me, {
      items: [
        {
          xtype: "gridpanel",
          border: false,
          autoScroll: true,
          stateful: true,
          stateId: "inv.inv-data-grid",
          bufferedRenderer: false,
          store: me.store,
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
            },
            {
              text: __("Description"),
              dataIndex: "description",
            },
            {
              text: __("Scope"),
              dataIndex: "scope",
            },
            {
              text: __("Type"),
              dataIndex: "type",
            },
            {
              text: __("Value"),
              dataIndex: "value",
              flex: 1,
              editor: "textfield",
              getEditor: me.onGetEditor,
              renderer: me.onValueRender,
            },
          ],
          features: [{
            ftype: "grouping",
          }],
          selType: "cellmodel",
          plugins: [
            Ext.create("Ext.grid.plugin.CellEditing", {
              clicksToEdit: 2,
            }),
          ],
          viewConfig: {
            enableTextSelection: true,
          },
          listeners: {
            scope: me,
            edit: me.onEdit,
          },
        },
      ],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this;
    me.currentId = data.id;
    me.store.loadData(data.data);
  },
  //
  onReload: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/data/",
      method: "GET",
      scope: me,
      success: function(response){
        me.preview(Ext.decode(response.responseText));
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  //
  onEdit: function(editor, e){
    var me = this,
      maskComponent = me.up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show("Saving data ..."),
      toReload = e.record.get("interface") === "Common" && e.record.get("name") === "Name";
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/data/",
      method: "PUT",
      jsonData: {
        "interface": e.record.get("interface"),
        "key": e.record.get("name"),
        "value": e.record.get("value"),
      },
      scope: me,
      success: function(){
        me.onReload();
        if(toReload){
          me.app.onReloadNav();
        }
      },
      failure: function(){
        NOC.error(__("Failed to save"));
      },
      callback: function(){
        maskComponent.hide(messageId);
      },
    });
  },
  //
  onGetEditor: function(record){
    if(record.get("is_const")){
      return false;
    }
    if(record.get("choices")){
      return {
        xtype: "combobox",
        store: record.get("choices"),
      }
    }
    switch(record.get("type")){
      case "int":
        return "numberfield";
      case "float":
        return "numberfield";
      default:
        return "textfield";
    }
  },
  //
  onValueRender: function(value, meta, record){
    if(record.get("name") === "Managed Object"){
      return this.up("panel").addIcon(value, "eye", __("Edit MO"), "sa.managedobject", record.get("item_id"));      
    }
    if(record.get("name") === "Model"){
      return this.up("panel").addIcon(value, "eye", __("Edit model"), "inv.objectmodel", record.get("item_id"));
    }
    if(record.get("is_const")){
      value = "<i class='fa fa-lock' style='padding-right: 4px;' title='" + __("Read only") + "'></i>" + value;
    } else{
      value = "<i class='fa fa-pencil' style='padding-right: 4px;'></i>" + (value || ""); 
    }
    if(record.get("type") === "bool"){
      return NOC.render.Bool(value);
    }
    if(record.get("name") === "ID"){
      return value + NOC.clipboardIcon(record.get("value"));
    }
    return value;
  },
  addIcon: function(value, icon, title, url, itemId){
    return `<i class='fa fa-${icon}' style='padding-right: 4px;cursor: pointer;' title='${title}' data-url='${url}' data-item-id='${itemId}'></i>${value}`;
  },
  //
  nameRenderer: function(value, meta, record){
    if(value === "ID"){
      return value + NOC.clipboardIcon(record.get("value"));
    }
    return value;
  },
  //
  afterRender: function(){
    var me = this;
    me.callParent(arguments);
    me.el.on("click", function(event, target){
      if(target.hasAttribute("data-url")){
        var recordId = target.getAttribute("data-item-id"),
          url = target.getAttribute("data-url");
        me.handleEyeClick(url, recordId);
      }
    }, me, {delegate: "[data-url]"});
  },
  //
  handleEyeClick: function(url, recordId){
    var showGrid = function(){
      var panel = this.up();
      if(panel){
        panel.close();
      }
    };
    NOC.launch(url, "history", {
      "args": [recordId],
      "override": [
        {"showGrid": showGrid},
      ],
    });
  },
});
