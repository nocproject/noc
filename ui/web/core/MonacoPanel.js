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
  viewModel: {
    formulas: {
      hasChanges: {
        bind: "{codeViewer.changes}",
        get: function(value){
          return value.length > 0;
        },
      },
    },
  },
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
      bind: {
        disabled: "{!hasChanges}",
      },
    },
    {
      itemId: "prevDiffBtn",
      glyph: NOC.glyph.arrow_up,
      tooltip: __("Previous change"),
      handler: "onPrevDiff",
      bind: {
        disabled: "{!hasChanges}",
      },
    },
    {
      glyph: NOC.glyph.exchange,
      tooltip: __("Swap contents"),
      handler: "onSwapRev",
      bind: {
        disabled: "{!hasChanges}",
      },
    },
    {
      text: __("Download"),
      tooltip: __("Download content"),
      glyph: NOC.glyph.download,
      handler: "onDownload",
    },
  ],
  items: [
    {
      xtype: "codeviewer",
      reference: "codeViewer",
      // codeviewer config
      language: "python",
      readOnly: true,
      automaticLayout: true,
    },
  ],
  preview: function(record, backItem){
    this.startPreview(record, backItem);
    if(Ext.isEmpty(this.restUrl)){
      var jsonData = JSON.stringify(record.data, null, 4);
      this.setContent(jsonData);
    } else{
      this.requestText(record);
    }
    this.requestRevisions();
    if(this.historyHashPrefix){
      this.app.setHistoryHash(
        record.get("id"),
        this.historyHashPrefix,
      );
    }
  },
  startPreview: function(record, backItem){
    var bi = backItem === undefined ? this.backItem : backItem;
    this.currentRecord = record;
    this.backItem = bi;
    this.setTitle(Ext.String.format(this.previewName, record.get("name")));
    this.fileName = Ext.String.format("{0}_{1}", Ext.util.Format.lowercase(record.get("pool__label")), record.get("address"));
  },
  requestText: function(record){
    this.rootUrl = Ext.String.format(this.restUrl, record.get("id"));
    this.mask(__("Loading"));
    Ext.Ajax.request({
      url: this.rootUrl,
      method: "GET",
      scope: this,
      success: function(response){
        var text = Ext.decode(response.responseText);
        this.setContent(text);
      },
      failure: function(){
        NOC.error(__("Failed to get text"));
      },
      callback: function(){
        this.unmask();
      },
    });
  },
  setContent: function(text){
    var codeViewer = this.down("codeviewer");
    if(Ext.isEmpty(codeViewer) || Ext.isEmpty(codeViewer.editor)) return;
    codeViewer.exitDiffMode(text);
  },
  requestRevisions: function(id){
    if(Ext.isEmpty(this.down("#revCombo"))) return;
    var url = (id ? Ext.String.format(this.restUrl, id) : this.rootUrl) + "revisions/";
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: this,
      success: function(response){
        var data = Ext.decode(response.responseText).map(function(item){
          return {
            id: item.id,
            ts_label: Ext.Date.format(Ext.Date.parse(item.ts, "c"), "Y-m-d H:i:s"),// "YYYY-MM-DD HH:mm:ss"
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
    this.down("#diffCombo").setValue(null);
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
      currentChangeIndex = this.getViewModel().get("codeViewer.currentChangeIndex"),
      changes = this.getViewModel().get("codeViewer.changes");
    if(!changes || changes.length === 0) return;
    var index = this.cyclePosition(currentChangeIndex, changes.length - 1, n),
      change = changes[index];
    this.getViewModel().set("codeViewer.currentChangeIndex", index);
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
  onDownload: function(){
    var blob = new Blob([this.down("codeviewer").getValue()], {type: "text/plain;charset=utf-8"}),
      revCombo = this.down("#revCombo"),
      suffix = revCombo.getDisplayValue().split(" ")[0].replace(/-/g, "") + ".conf.txt";
    NOC.saveAs(blob, this.fileName + "_" + suffix);
  },
  onSwapRev: function(){
    var revCombo = this.down("#revCombo"),
      diffCombo = this.down("#diffCombo"),
      revValue = revCombo.getValue(),
      diffValue = diffCombo.getValue();
    if(!revValue || !diffValue) return;
    revCombo.setValue(diffValue);
    diffCombo.setValue(revValue);
    this.swapContents();
  },
  swapContents: function(){
    var editor = this.down("codeviewer").editor;
    if(editor && Ext.isDefined(editor.getModel().modified)){ // check if in diff mode
      var originalModel = editor.getModel().original,
        modifiedModel = editor.getModel().modified;
      editor.setModel({
        original: modifiedModel,
        modified: originalModel,
      });
    }
  },
  cyclePosition: function(current, max, step){
    var newValue = current + step;
  
    if(newValue < 0){
      return max;
    } else if(newValue > max){
      return 0;
    }
    return newValue;
  },
});