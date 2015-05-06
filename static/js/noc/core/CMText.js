//---------------------------------------------------------------------
// NOC.core.CMText
// CodeMirror textarea
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.CMTextLayout");

Ext.define("NOC.core.CMTextLayout", {
    extend: "Ext.layout.component.field.FieldContainer",
    alias: ["layout.cmtext"],
    renderItems: Ext.emptyFn,
    type: "cmtext",

    beginLayout: function (ownerContext) {
        var me = this;
        me.callParent(arguments);
        ownerContext.editorContext = ownerContext.getEl("containerEl");
    },

    publishInnerHeight: function (ownerContext, height) {
        var me = this;
        ownerContext.editorContext.setHeight(height, true);
    }
});

console.debug("Defining NOC.core.CMText");
Ext.define("NOC.core.CMText", {
    extend: "Ext.form.field.Base",
    alias: "widget.cmtext",
    componentLayout: "cmtext",
    readOnly: false,
    lineNumbers: true,
    mode: null,
    childEls: [
        "containerEl"
    ],

    fieldSubTpl: [
        '<div id="{cmpId}-containerEl" class="{editorCls}" data-ref="containerEl" style="{size}"></div>',
        {
            disableFormats: true
        }
    ],

    editorWrapCls: Ext.baseCSSPrefix + 'html-editor-wrap ' + Ext.baseCSSPrefix + 'html-editor-input',

    initComponent: function () {
        var me = this;
        me.editor = null;
        me.rawValue = null;
        me.callParent();
        me.initLabelable();
        me.initField();
        me.on("resize", me.onFieldResize, me);
        me.on("beforedestroy", me.onBeforeDestroy, me);
    },

    afterRender: function () {
        var me = this;

        me.callParent(arguments);
        me.initEditor();
    },

    onFieldResize: function () {
        var me = this;

        if (me.editor) {
            me.editor.refresh();
        }
    },

    getSubTplData: function () {
        var me = this,
            cssPrefix = Ext.baseCSSPrefix;

        return {
            $comp: me,
            cmpId: me.id,
            id: me.getInputId(),
            toolbarWrapCls: cssPrefix + 'html-editor-tb',
            textareaCls: cssPrefix + 'hidden',
            editorCls: cssPrefix + 'codemirror ' + me.editorWrapCls,
            editorName: Ext.id(),
            size: 'height:100px;width:100%'
        };
    },

    initEditor: function () {
        var me = this;

        // Create CodeMirror
        CodeMirror.modeURL = "/static/pkg/codemirror/mode/%N/%N.js";
        me.editor = new CodeMirror(me.containerEl.dom, {
            readOnly: me.readOnly,
            lineNumbers: me.lineNumbers,
            styleActiveLine: true,
            value: me.rawValue || "",
        });
        me.setMode(me.mode);
        // change the codemirror css
        var css = Ext.util.CSS.getRule(".CodeMirror");
        if (css) {
            css.style.height = "100%";
            css.style.position = "relative";
            css.style.overflow = "hidden";
        }
        css = Ext.util.CSS.getRule(".CodeMirror-Scroll");
        if (css) {
            css.style.height = "100%";
        }
        me.setTheme(NOC.settings.preview_theme);
    },

    // Set CodeMirror theme
    setTheme: function (name) {
        var me = this;
        if (name !== "default") {
            Ext.util.CSS.swapStyleSheet(
                "cmcss-" + me.id,  // Fake one
                "/static/pkg/codemirror/theme/" + name + ".css"
            );
        }
        me.editor.setOption("theme", name);
    },

    renderText: function (text, syntax) {
        var me = this;
        syntax = syntax || null;
        text = text || "NO DATA";
        CodeMirror.modeURL = "/static/pkg/codemirror/mode/%N/%N.js";
        me.editor.setValue(text);
        if (syntax) {
            me.editor.setOption("mode", syntax);
            CodeMirror.autoLoadMode(me.editor, syntax);
        }
    },

    setValue: function (value) {
        var me = this;
        me.rawValue = value;
        if (me.editor) {
            me.renderText(value);
        }
        return me;
    },

    getValue: function () {
        var me = this;
        return me.editor ? me.editor.getValue() : null;
    },

    getRawValue: function () {
        var me = this;
        return me.getValue();
    },

    getSubmitValue: function () {
        var me = this;
        return me.getValue();
    },

    onBeforeDestroy: function () {
        var me = this;
        me.un("resize", me.onFieldResize, me);
        if (me.editor) {
            try {
                delete me.editor;
            } catch (e) {
            }
            Ext.destroyMembers("containerEl");
        }
    },

    setMode: function(mode) {
        var me = this;
        me.mode = mode;
        if(me.mode) {
            CodeMirror.autoLoadMode(me.editor, me.mode);
            me.editor.setOption("mode", me.mode);
        }
    },

    scrollDown: function() {
        var me = this;
        me.editor.setCursor(me.editor.lineCount() - 1, 0);
    }
});
