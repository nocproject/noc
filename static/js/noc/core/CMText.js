//---------------------------------------------------------------------
// NOC.core.CMText
// CodeMirror textarea
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.CMText");

Ext.define("NOC.core.CMText", {
    extend: "Ext.form.field.Base",
    alias: "widget.cmtext",
    readOnly: false,
    lineNumbers: true,

    childEls: [
        "editorEl"
    ],

    fieldSubTpl: [
        '<div id="{cmpId}-editorEl" class="{editorCls}" data-ref="editorEl" style="{size}"></div>',
        {
            disableFormats: true
        }
    ],

    editorWrapCls: Ext.baseCSSPrefix + 'html-editor-wrap ' + Ext.baseCSSPrefix + 'html-editor-input',

    initComponent: function () {
        var me = this;
        me.viewer = null;
        me._value = null;
        me.callParent();
        me.initLabelable();
        me.initField();
        me.on("resise", me.onFieldResize, me);
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
        me.viewer = new CodeMirror(me.editorEl.dom, {
            readOnly: me.readOnly,
            lineNumbers: me.lineNumbers,
            styleActiveLine: true
        });
        // change the codemirror css
        var css = Ext.util.CSS.getRule(".CodeMirror");
        if (css) {
            css.style.height = "100%";
            css.style.position = "relative";
            css.style.overflow = "hidden";
        }
        css = Ext.util.CSS.getRule('.CodeMirror-Scroll');
        if (css) {
            css.style.height = '100%';
        }
        me.setTheme(NOC.settings.preview_theme);
        if(me._value !== null) {
            me.setValue(me._value);
            me._value = null;
        }
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
        me.viewer.setOption("theme", name);
    },
    renderText: function (text, syntax) {
        var me = this;
        syntax = syntax || null;
        text = text || "NO DATA";
        CodeMirror.modeURL = "/static/pkg/codemirror/mode/%N/%N.js";
        me.viewer.setValue(text);
        if (syntax) {
            me.viewer.setOption("mode", syntax);
            CodeMirror.autoLoadMode(me.viewer, syntax);
        }
    },

    setValue: function (value) {
        var me = this;
        if(me.viewer === null) {
            me._value = value;
        } else {
            me.renderText(value);
        }
    }
});
