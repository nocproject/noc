Ext.define("NOC.core.CodeViewer", {
  extend: "Ext.Component",
  alias: "widget.codeviewer",
  type: "codeviewer",
  mixins: [
    "Ext.form.Labelable",
    "Ext.form.field.Field",
  ],
 
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
    
    return me;
  },

  setValue: function(value){
    var me = this;
    me.value = value || "";
        
    if(me.editor){
      me.editor.setValue(me.value);
    }
        
    return me;
  },
    
  getValue: function(){
    var me = this;
        
    if(me.editor){
      return me.editor.getValue();
    }
        
    return me.value;
  },
    
  setLanguage: function(language){
    var me = this;
    me.language = language;
        
    if(me.editor){
      window.monaco.editor.setModelLanguage(me.editor.getModel(), language);
    }
        
    return me;
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
});