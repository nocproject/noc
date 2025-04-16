//---------------------------------------------------------------------
// NOC.core.MonacoPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.MonacoPanel");

Ext.define("NOC.core.MonacoPanel", {
  extend: "NOC.core.ApplicationPanel",
  alias: "widget.core.monacopanel",
  requires: [
    "NOC.core.CodeViewer",
  ],
  defaultListenerScope: true,
  layout: "fit",
  tbar: [
    {
      itemId: "close",
      text: __("Close"),
      glyph: NOC.glyph.arrow_left,
      handler: "onBack",
    },
    {
      glyph: NOC.glyph.refresh,
      text: __("Reset"),
      tooltip: __("Reset"),
      handler: "onReset",
    },
    "-",
    {
      xtype: "combo",
      fieldLabel: __("Version"),
      itemId: "revCombo",
      queryMode: "local",
      displayField: "ts_label",
      valueField: "id",
      labelWidth: 75,
      width: 300,
      store: {
        fields: [
          {
            name: "id",
            type: "auto",
          },
          {
            name: "ts",
            type: "date",
          },
          {
            name: "ts_label",
          },
        ],
        data: [],
      },
      listeners: {
        select: "onSelectRev",
        specialkey: "onRevSpecialKey",
      },
    },
    {
      xtype: "combo",
      itemId: "diffCombo",
      fieldLabel: __("Compare"),
      queryMode: "local",
      displayField: "ts_label",
      valueField: "id",
      labelWidth: 85,
      width: 300,
      store: {
        fields: [
          {
            name: "id",
            type: "auto",
          },
          {
            name: "ts",
            type: "date",
          },
          {
            name: "ts_label",
          },
        ],
        data: [],
      },
      listeners: {
        select: "onSelectDiff",
        specialkey: "onDiffSpecialKey",
      },
    },
    "-",
    {
      itemId: "nextDiffBtn",
      glyph: NOC.glyph.arrow_down,
      tooltip: __("Next change"),
      handler: "onNextDiff",
      //   bind: {
      // disabled: "{!canNextChange}",
      //   },
    },
    {
      itemId: "prevDiffBtn",
      glyph: NOC.glyph.arrow_up,
      tooltip: __("Previous change"),
      handler: "onPrevDiff",
      //   bind: {
      //     disabled: "{!canPrevChange}",
      //   },
    },
  ],
  items: [
    {
      xtype: "codeviewer",
      // codeviewer config
      language: "python",
      readOnly: true,
      automaticLayout: true,
      theme: "vs-dark",
    },
  ],
  preview: function(record, backItem){
    this.startPreview(record, backItem);
    this.requestText();
    this.requestRevisions();
    if(this.historyHashPrefix){
      this.app.setHistoryHash(
        record.get("id"),
        this.historyHashPrefix,
      );
    }
  },
  startPreview: function(record, backItem){
    var me = this,
      bi = backItem === undefined ? me.backItem : backItem;
    me.currentRecord = record;
    me.backItem = bi;
    me.rootUrl = Ext.String.format(me.restUrl, record.get("id"));
    me.setTitle(Ext.String.format(me.previewName, record.get("name")));
    me.fileName = Ext.String.format("{0}_{1}", Ext.util.Format.lowercase(record.get("pool__label")), record.get("address"));
  },
  requestText: function(){
    this.mask(__("Loading"));
    Ext.Ajax.request({
      url: this.rootUrl,
      method: "GET",
      scope: this,
      success: function(response){
        var text = Ext.decode(response.responseText);
        this.down("codeviewer").setValue(text);
      },
      failure: function(){
        NOC.error(__("Failed to get text"));
      },
      callback: function(){
        this.unmask();
      },
    });
  },
  requestRevisions: function(id){
    var currentTZ = moment.tz.guess(),
      url = (id ? Ext.String.format(this.restUrl, id) : this.rootUrl) + "revisions/";
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: this,
      success: function(response){
        var data = Ext.decode(response.responseText).map(function(item){
          return {
            id: item.id,
            ts_label: moment.tz(item.ts, NOC.settings.timezone).clone().tz(currentTZ).format("YYYY-MM-DD HH:mm:ss"),
            ts: item.ts,
          }
        });

        if(id === undefined){
          var revCombo = this.down("#revCombo"),
            diffCombo = this.down("#diffCombo");
          revCombo.setValue(null);
          revCombo.store.loadData(data);
          if(data.length > 0){
            revCombo.select([revCombo.store.getAt(0)]);
          }
        }
        diffCombo.setValue(null);
        // me.sideBySideModeButton.toggle(false);
        diffCombo.store.loadData(data);
      },
      failure: function(){
        NOC.error(__("Failed to get revisions"));
      },
    });
  },
  requestRevision: function(rev, callback){
    this.mask(__("Loading"));
    Ext.Ajax.request({
      url: this.rootUrl + rev + "/",
      method: "GET",
      scope: this,
      success: callback,
      failure: function(){
        NOC.error(__("Failed to get text"));
      },
      callback: function(){
        this.unmask();
      },
    });
  },
  renderText: function(text){
    text = text || "NO DATA";
    this.down("codeviewer").exitDiffMode(text);
  },
  renderDiff: function(text){
    var viewer = this.down("codeviewer"),
      editor = viewer.editor;
      
    if(editor && editor.getModel && editor.getModel().original){
      viewer.updateDiffModified(text);
    } else{
      var origText = viewer.getValue()
      viewer.showDiff(origText, text);
    }
  },
  onSelectRev: function(combo, record){
    this.requestRevision(record.get("id"), function(response){
      this.renderText(Ext.decode(response.responseText));
    });
  },
  onSelectDiff: function(combo, record){
    this.requestRevision(record.get("id"), function(response){
      this.renderDiff(Ext.decode(response.responseText));
    });
  },
  onRevSpecialKey: function(combo, evt){
    if(evt.getKey() === evt.ESC){
      combo.clearValue();
    }
  },
  onDiffSpecialKey: function(combo, evt){
    var me = this;
    if(evt.getKey() === evt.ESC){
      var revCombo = me.down("#revCombo");
      combo.clearValue();
      me.requestRevision(revCombo.getPicker().getSelectionModel().lastSelected.get("id"),
                         function(response){
                           this.renderText(Ext.decode(response.responseText));
                         });
    }
  },
  onBack: function(){
    this.onClose();
  },
  onReset: function(){
    this.requestText();
    this.requestRevisions();
  },
  setChange: function(n){
    var codeViewer = this.down("codeviewer"),
      diffEditor = codeViewer.editor,
      changes = codeViewer.changes;
    if(!changes || changes.length === 0) return;
    codeViewer.currentChangeIndex = (codeViewer.currentChangeIndex + n) % changes.length;
    if(codeViewer.currentChangeIndex < 0) return;
    var change = changes[codeViewer.currentChangeIndex];
    diffEditor.getModifiedEditor().revealLineInCenter(change.modifiedStartLineNumber);
    diffEditor.getModifiedEditor().setPosition({
      lineNumber: change.modifiedStartLineNumber,
      column: 1,
    });
    // var modifiedEditor = diffEditor.getModifiedEditor();
    // modifiedEditor.setSelections({
    //   positionColumn: change.modifiedEndLineNumber,
    //   positionLineNumber: 1,
    //   selectionStartLineNumber: change.modifiedStartLineNumber,
    //   selectionEndColumn: 1,
    // });
  },
  onNextDiff: function(){
    this.setChange(1);
  },
  onPrevDiff: function(){
    this.setChange(-1);
  },
});