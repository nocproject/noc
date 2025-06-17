Ext.define("NOC.core.MarkdownEditor", {
  extend: "Ext.Component",
  alias: "widget.markdowneditor",
    
  config: {
    value: "",
    language: "markdown",
    theme: "vs",
  },

  afterRender: function(){
    this.callParent(arguments);
    this.initMonaco();
  },

  initMonaco: function(){
    var me = this;
    var editorContainer = me.getEl().dom;
    me.editor = window.monaco.editor.create(editorContainer, {
      value: me.getValue(),
      language: me.getLanguage(),
      theme: me.getTheme(),
      automaticLayout: true,
      minimap: {enabled: false},
      scrollBeyondLastLine: false,
    });

    me.editor.onDidChangeModelContent(function(){
      var newValue = me.editor.getValue();
      //   me.setValue(newValue);
      me.fireEvent("change", me, newValue);
    });
  },

  setValue: function(value){
    this.callParent([value]);
    if(this.editor){
      this.editor.setValue(value);
    }
  },

  getValue: function(){
    return this.editor ? this.editor.getValue() : this.callParent();
  },

  destroy: function(){
    if(this.editor){
      this.editor.dispose();
      this.editor = null;
    }
    this.callParent();
  },
});