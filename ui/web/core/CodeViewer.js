//---------------------------------------------------------------------
// NOC.core.CodeViewer
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.CodeViewer");

Ext.define("NOC.core.CodeViewer", {
  extend: "Ext.Component",
  alias: "widget.codeviewer",
  type: "codeviewer",
  mixins: [
    "Ext.form.Labelable",
    "Ext.form.field.Field",
  ],

  publishes: ["changes", "currentChangeIndex"],
  config: {
    changes: [],
    currentChangeIndex: 0,
  },
  language: "javascript",
  value: "",
  readOnly: false,
  theme: "vs",
  automaticLayout: true,
    
  editor: null,
  changeListeners: null,
  
  initComponent: function(){
    var me = this;
    me.callParent(arguments);
        
    me.changeListeners = [];
    me.addCls("noc-code-viewer");
  },
    
  afterRender: function(){
    var me = this;
    me.callParent(arguments);
        
    me.initEditor();
  },
    
  initEditor: function(){
    var me = this;
        
    if(!window.monaco){
      console.error("Monaco Editor is not loaded");
      return;
    }
        
    me.editor = window.monaco.editor.create(me.el.dom, {
      value: me.value,
      language: me.language,
      readOnly: me.readOnly,
      theme: me.theme,
      automaticLayout: me.automaticLayout,
    });
    me.setChanges([]);
    me.setCurrentChangeIndex(0);
    if(me.editor){
      var disposable = me.editor.onDidChangeModelContent(function(event){
        me.value = me.editor.getValue();
        me.fireEvent("contentchanged", me, me.value, event);
        
        if(typeof me.contentChanged === "function"){
          me.contentChanged(me, me.value, event);
        }
      });
      
      me.changeListeners.push(disposable);
    }
 
    me.on("resize", function(){
      if(me.editor){
        me.editor.layout();
      }
    });
  },
  
  onContentChange: function(fn, scope){
    var me = this;
    
    if(typeof fn === "function"){
      me.contentChanged = scope ? Ext.bind(fn, scope) : fn;
    }
  },

  setValue: function(value){
    this.value = value || "";
        
    if(this.editor){
      this.editor.setValue(this.value);
    }
  },
    
  getValue: function(){
    if(this.editor && Ext.isDefined(this.editor.getModel().modified)){ // check if in diff mode
      return this.editor.getModel().original.getValue();
    }

    if(this.editor){
      return this.editor.getValue();
    }
        
    return this.value;
  },
    
  setLanguage: function(language){
    var me = this;
    me.language = language;
        
    if(me.editor){
      window.monaco.editor.setModelLanguage(me.editor.getModel(), language);
    }
  },
    
  onDestroy: function(){
    var me = this;
        
    if(me.editor){
      if(me.changeListeners && me.changeListeners.length){
        Ext.Array.each(me.changeListeners, function(listener){
          if(listener && typeof listener.dispose === "function"){
            listener.dispose();
          }
        });
        me.changeListeners = [];
      }
      
      me.editor.dispose();
      me.editor = null;
    }
        
    me.callParent(arguments);
  },
  showDiff: function(originalText, modifiedText){
    var me = this;
    
    if(me.editor){
      if(me.changeListeners && me.changeListeners.length){
        Ext.Array.each(me.changeListeners, function(listener){
          if(listener && typeof listener.dispose === "function"){
            listener.dispose();
          }
        });
        me.changeListeners = [];
      }
      
      me.editor.dispose();
      me.editor = null;
    }
    
    me.editor = window.monaco.editor.createDiffEditor(me.el.dom, {
      automaticLayout: me.automaticLayout,
      readOnly: me.readOnly,
      theme: me.theme,
      renderSideBySide: true,
    });
    
    var originalModel = window.monaco.editor.createModel(originalText || "", me.language),
      modifiedModel = window.monaco.editor.createModel(modifiedText || me.value, me.language);
    
    me.editor.setModel({
      original: originalModel,
      modified: modifiedModel,
    });
   
    me.changeListeners.push(me.editor.onDidUpdateDiff(() => {
      var changes = me.editor.getLineChanges() || [];
      me.setChanges(changes);
      me.setCurrentChangeIndex(0);
      if(changes.length > 0){
        var change = changes[0];
        me.editor.getModifiedEditor().revealLineInCenter(change.modifiedStartLineNumber);
        me.editor.getModifiedEditor().setPosition({
          lineNumber: change.modifiedStartLineNumber,
          column: 1,
        });
      }
    }));
    me.value = modifiedText || me.value;
  },
  updateDiffModified: function(modifiedText){
    var diffModel = this.editor.getModel(),
      newModifiedModel = window.monaco.editor.createModel(modifiedText || "", this.language);
    
    this.editor.setModel({
      original: diffModel.original,
      modified: newModifiedModel,
    });
    
    diffModel.modified.dispose();
    
    this.value = modifiedText || "";
  },
  exitDiffMode: function(text){
    var me = this;
    
    if(me.editor){
      if(me.changeListeners && me.changeListeners.length){
        Ext.Array.each(me.changeListeners, function(listener){
          if(listener && typeof listener.dispose === "function"){
            listener.dispose();
          }
        });
        me.changeListeners = [];
      }
      
      me.editor.dispose();
      me.editor = null;
    }
    
    me.initEditor();
    me.setValue(text);
  },
  
  scrollDown: function(){
    var model, lineCount, lastLine, lastLineContent, lastColumn, position;
    
    if(!this.editor){
      return;
    }
    
    model = this.editor.getModel();
    if(!model){
      return;
    }
    
    lineCount = model.getLineCount();
    lastLine = lineCount > 0 ? lineCount : 1;
    lastLineContent = model.getLineContent(lastLine);
    lastColumn = lastLineContent.length + 1;
    
    position = {
      lineNumber: lastLine,
      column: lastColumn,
    };
    
    this.editor.setPosition(position);
    
    this.editor.revealPosition(position, window.monaco.editor.ScrollType.Immediate);
  },
});