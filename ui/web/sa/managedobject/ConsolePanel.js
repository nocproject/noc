//---------------------------------------------------------------------
// sa.managed_object ConsolePanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.ConsolePanel");

Ext.define("NOC.sa.managedobject.ConsolePanel", {
  extend: "Ext.panel.Panel",
  requires: [],
  app: null,
  alias: "widget.sa.console",
  layout: "fit",
  autoScroll: true,

  initComponent: function(){
    var me = this;

    me.prompt = "> ";
    me.cmdHistory = [];
    me.cmdIndex = null;

    me.cmdField = Ext.create("Ext.form.field.Text", {
      anchor: "100%",
      fieldLabel: __(">"),
      labelWidth: 16,
      itemId: "cmdfield",
      listeners: {
        scope: me,
        specialkey: me.onSpecialKey,
      },
    });

    me.consoleBody = Ext.create("NOC.core.CodeViewer", {
      readOnly: true,
      theme: "vs-dark",
    });

    me.closeButton = Ext.create("Ext.button.Button", {
      text: __("Close"),
      glyph: NOC.glyph.arrow_left,
      scope: me,
      handler: me.onClose,
    });

    me.clearButton = Ext.create("Ext.button.Button", {
      text: __("Clear"),
      glyph: NOC.glyph.eraser,
      scope: me,
      handler: me.clearBody,
    });

    Ext.apply(me, {
      items: [
        me.consoleBody,
      ],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [
            me.closeButton,
            "-",
            me.clearButton,
          ],
        },
        {
          xtype: "toolbar",
          dock: "bottom",
          layout: "fit",
          items: [
            me.cmdField,
          ],
        },
      ],
    });
    me.callParent();
  },
  //
  preview: function(record){
    var me = this,
      c = [record.get("name"), "console"],
      platform = record.get("platform");
    if(platform){
      c.push("(" + platform + ")");
    }
    me.currentRecord = record;
    me.setTitle(c.join(" "));
    me.clearBody();
    me.prompt = record.get("name") + "> ";
    if(me.historyHashPrefix){
      me.app.setHistoryHash(
        me.currentRecord.get("id"),
        me.historyHashPrefix,
      );
    }
  },
  //
  onSpecialKey: function(field, e){
    var me = this;
    switch(e.getKey()){
      case e.ENTER:
        me.submitCommand(field.getValue());
        field.setValue("");
        break;
      case e.ESC:
        field.setValue("");
        break;
      case e.UP:
        if(me.cmdIndex !== null){
          me.cmdIndex = Math.max(0, me.cmdIndex - 1);
          field.setValue(me.cmdHistory[me.cmdIndex]);
        }
        break;
      case e.DOWN:
        if(me.cmdIndex !== null){
          me.cmdIndex = Math.min(
            me.cmdIndex + 1,
            me.cmdHistory.length - 1);
          field.setValue(me.cmdHistory[me.cmdIndex]);
        }
        break;
    }
  },
  //
  submitCommand: function(cmd){
    var me = this;

    // Maintain history
    if(me.cmdHistory.length === 0 || me.cmdHistory[me.cmdHistory.length - 1] != cmd){
      me.cmdHistory.push(cmd);
    }
    me.cmdIndex = me.cmdHistory.length;
    // Display
    me.consoleOut(me.prompt + cmd);
    Ext.Ajax.request({
      url: "/sa/managedobject/" + me.currentRecord.get("id") + "/console/",
      method: "POST",
      scope: me,
      jsonData: {
        commands: [cmd],
        ignore_cli_errors: true,
      },
      success: function(response){
        var data = Ext.decode(response.responseText);
        if(data.error){
          // Exception
          me.consoleOut("%ERROR: " + data.error);
        } else{
          me.consoleOut(data.result.output);
        }
      },
      failure: function(){
        NOC.error(__("Failed to run command"));
      },
    });
  },
  //
  clearBody: function(){
    var me = this;
    me.consoleBody.setValue("Welcome to the " + me.currentRecord.get("name") + " console!\n");
  },
  //
  onClose: function(){
    var me = this;
    me.app.showForm();
  },

  consoleOut: function(v){
    var me = this;
    me.consoleBody.setValue(
      me.consoleBody.getValue() + v + "\n",
    );
    me.consoleBody.scrollDown();
  },

  getDefaultFocus: function(){
    var me = this;
    return me.cmdField;
  },
});
