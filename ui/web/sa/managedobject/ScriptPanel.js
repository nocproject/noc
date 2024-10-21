//---------------------------------------------------------------------
// sa.managedobject ScriptPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.ScriptPanel");

Ext.define("NOC.sa.managedobject.ScriptPanel", {
  extend: "NOC.core.ApplicationPanel",
  alias: "widget.sa.script",
  requires: [
    "NOC.sa.managedobject.ScriptStore",
    "NOC.sa.managedobject.scripts.ErrorPreview",
    "Ext.ux.form.SearchField",
  ],
  app: null,
  autoScroll: true,
  //
  listeners: {
    activate: function(self){
      if(self.scriptContainer){
        self.scriptContainer.getLayout().setActiveItem(0);
      }
    },
  },
  //
  initComponent: function(){
    var me = this;

    me.currentObject = null;
    me.currentPreview = null;
    me.form = null;

    me.scriptStore = Ext.create("NOC.sa.managedobject.ScriptStore");

    me.searchField = Ext.create({
      xtype: "searchfield",
      name: "search_field",
      scope: me,
      handler: me.onSearch,
    });

    me.scriptPanel = Ext.create("Ext.grid.Panel", {
      store: me.scriptStore,
      columns: [
        {
          text: __("Script"),
          dataIndex: "name",
          flex: 1,
          renderer: function(value, meta, record){
            if(record.get("has_input")){
              return value + "...";
            } else{
              return value;
            }
          },
        },
      ],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [
            me.getCloseButton(),
            "-",
            me.searchField,
          ],
        },
      ],
      listeners: {
        scope: me,
        celldblclick: me.onRunScript,
      },
    });

    me.scriptContainer = Ext.create("Ext.panel.Panel", {
      layout: "card",
      items: [me.scriptPanel],
    });
    //
    Ext.apply(me, {
      items: [me.scriptContainer],
    });
    me.callParent();
    me.loadMask = new Ext.LoadMask({target: me, msg: "Running task. Please wait ..."});
  },
  //
  preview: function(record, backItem){
    var me = this;
    me.callParent(arguments);
    me.setTitle(record.get("name") + " scripts");
    Ext.Ajax.request({
      url: "/sa/managedobject/" + record.get("id") + "/scripts/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        me.scriptStore.loadData(data || []);
      },
      failure: function(){
        NOC.error(__("Failed to load data"));
      },
    });
  },
  //
  onRunScript: function(grid, td, cellIndex, record, tr, rowIndex, e, eOpts){
    var me = this,
      hi = record.get("has_input"),
      ri = record.get("require_input");
    me.currentPreview = record.get("preview");
    if(!hi || (e.altKey && !ri)){
      me.runScript(record.get("name"));
    } else{
      me.showForm(record.get("name"), record.get("form"));
    }
  },
  //
  runScript: function(name, params){
    var me = this;
    params = params || {};
    me.loadMask.show();
    Ext.Ajax.request({
      url: "/sa/managedobject/" + me.currentRecord.get("id") + "/scripts/" + name + "/",
      method: "POST",
      scope: me,
      jsonData: params,
      success: function(response){
        var data = Ext.decode(response.responseText);
        me.loadMask.hide();
        if(data.error){
          me.showError(name, data.error)
        } else{
          me.showResult(name, data.result)
        }
      },
      failure: function(){
        me.loadMask.hide();
        NOC.error(__("Failed to run script"));
      },
    });
  },
  //
  showResult: function(name, result){
    var me = this,
      preview = Ext.create(me.currentPreview, {
        app: me,
        itemId: "sa-script-result",
        script: name,
        result: result,
      });
    Ext.each(me.scriptContainer.query('[itemId=sa-script-result]'), function(comp){
      me.scriptContainer.remove(comp);
    })
    me.scriptContainer.add(preview);
    me.scriptContainer.setActiveItem("sa-script-result");
  },
  //
  showError: function(name, result){
    var me = this,
      preview = Ext.create("NOC.sa.managedobject.scripts.ErrorPreview", {
        app: me,
        itemId: "sa-script-error",
        script: name,
        result: result,
      });
    Ext.each(me.scriptContainer.query('[itemId=sa-script-error]'), function(comp){
      me.scriptContainer.remove(comp);
    })
    me.scriptContainer.add(preview);
    me.scriptContainer.setActiveItem("sa-script-error");
  },
  //
  showForm: function(name, items){
    var me = this, queryResult;
    me.form = Ext.create("Ext.form.Panel", {
      itemId: "sa-script-form",
      items: items,
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [
            {
              text: __("Close"),
              glyph: NOC.glyph.arrow_left,
              scope: me,
              handler: me.onFormClose,
            },
            "-",
            {
              text: __("Run"),
              glyph: NOC.glyph.play,
              scope: me,
              handler: Ext.bind(me.onFormRun, me, [name]),
            },
          ],
        },
      ],
    });
    Ext.each(me.scriptContainer.query('[itemId=sa-script-form]'), function(comp){
      me.scriptContainer.remove(comp);
    })
    me.scriptContainer.add(me.form);
    me.scriptContainer.setActiveItem('sa-script-form');
  },
  //
  destroyForm: function(){
    var me = this;
    me.scriptContainer.setActiveItem(0);
  },
  //
  onFormClose: function(){
    var me = this;
    me.destroyForm();
  },
  //
  onFormRun: function(name){
    var me = this,
      params = {},
      values;

    if(!me.form.isValid()){
      return;
    }
    values = me.form.getValues();
    Ext.Object.each(values, function(n){
      var v = values[n];
      if(!v){
        return;
      }
      if(typeof v === "string" && !v.length){
        return;
      }
      params[n] = v;
    });
    me.destroyForm();
    me.runScript(name, params);
  },
  //
  onSearch: function(value){
    var me = this;
    me.scriptStore.clearFilter(true);
    me.scriptStore.filterBy(function(record){
      return record.get("name").indexOf(value) !== -1;
    }, me);
  },
});
