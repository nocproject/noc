//---------------------------------------------------------------------
// NOC.core.Preview
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Preview");

Ext.define("NOC.core.Preview", {
    extend: "NOC.core.ApplicationPanel",
    msg: "",
    layout: "fit",
    syntax: null,
    app: null,
    restUrl: null,

    initComponent: function() {
        var me = this;


        me.cmContainer = Ext.create({
            xtype: "container",
            layout: "fit",
            tpl: [
                '<div id="{cmpId}-cmEl" class="{cmpCls}" style="{size}"></div>'
            ],
            data: {
                cmpId: me.id,
                cmpCls: Ext.baseCSSPrefix + "codemirror " + Ext.baseCSSPrefix + 'html-editor-wrap ' + Ext.baseCSSPrefix + 'html-editor-input',
                size: "width:100%;height:100%"
            }
        });

        Ext.apply(me, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    {
                        itemId: "close",
                        text: "Close",
                        glyph: NOC.glyph.arrow_left,
                        scope: me,
                        handler: me.onClose
                    },
                    me.revCombo,
                    me.diffCombo
                ]
            }],
            items: [me.cmContainer],
            listeners: {
                scope: me,
                resize: me.onResize
            }
        });
        me.callParent();
        //
        me.urlTemplate = Handlebars.compile(me.restUrl);
        me.titleTemplate = Handlebars.compile(me.previewName);
    },
    afterRender: function() {
        var me = this;
        me.callParent(arguments);
        me.initViewer();
    },
    //
    initViewer: function() {
        var me = this,
            el = me.cmContainer.el.getById(me.id + "-cmEl", true);
        // Create CodeMirror
        me.viewer = new CodeMirror(el, {
            readOnly: true,
            lineNumbers: true
        });
        // change the codemirror css
        var css = Ext.util.CSS.getRule(".CodeMirror");
        if(css){
            css.style.height = "100%";
            css.style.position = "relative";
            css.style.overflow = "hidden";
        }
        css = Ext.util.CSS.getRule('.CodeMirror-Scroll');
        if(css){
            css.style.height = '100%';
        }
    },
    //
    preview: function(record) {
        var me = this;
        me.currentRecord = record;
        me.rootUrl = Ext.String.format(me.restUrl, record.get("id"));
        me.rootUrl = me.urlTemplate(record.data);
        me.setTitle(me.titleTemplate(record.data));
        me.requestText();
    },
    //
    requestText: function() {
        var me = this;
        Ext.Ajax.request({
            url: me.rootUrl,
            method: "GET",
            scope: me,
            success: function(response) {
                me.renderText(Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.error("Failed to get text");
            }
        });
    },
    //
    renderText: function(text) {
        var me = this;
        me.viewer.setValue(text);
    },
    //
    onClose: function() {
        var me = this;
        me.app.showGrid();
    },
    //
    onResize: function() {
        var me = this;
        if(me.viewer) {
            me.viewer.refresh();
        }
    }
});
