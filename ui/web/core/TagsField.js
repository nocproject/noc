//---------------------------------------------------------------------
// NOC.core.TagsField -
// Tags Field
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.TagsField");

Ext.define("NOC.core.TagsField", {
    extend: "Ext.form.field.Tag",
    alias: "widget.tagsfield",
    displayField: "label",
    valueField: "id",
    queryParam: "__query",
    queryMode: "remote",
    autoLoadOnValue: true,
    filterPickList: true,
    forceSelection: false,
    createNewOnEnter: true,
    triggers: {
        toBuffer: {
            cls: "fas fa fa-clipboard",
            hidden: false,
            weight: -1,
            handler: "toClipboard"
        }
    },
    initComponent: function() {
        var me = this,
            store = me.store || {
                fields: ["id", "label"],
                pageSize: 25,
                proxy: {
                    type: "rest",
                    url: '/main/label/lookup/',
                    pageParam: "__page",
                    startParam: "__start",
                    limitParam: "__limit",
                    sortParam: "__sort",
                    extraParams: {
                        "__format": "ext"
                    },
                    reader: {
                        type: "json",
                        rootProperty: "data",
                        totalProperty: "total",
                        successProperty: "success"
                    }
                }
            };
        Ext.apply(me, {
            store: store
        });
        me.callParent();
    },
    toClipboard: function(btn) {
        var writeText = function(btn) {
            var text = btn.getValue().join(","),
                tagsEl = btn.el.query(".x-tagfield-list"),
                selectElementText = function(el) {
                    var range = document.createRange(),
                        selection = window.getSelection();
                    range.selectNode(el);
                    selection.removeAllRanges();
                    selection.addRange(range);
                },
                listener = function(e) {
                    if(e.clipboardData && Ext.isFunction(e.clipboardData.setData)) {
                        e.clipboardData.setData("text/plain", text);
                    } else { // IE 11
                        clipboardData.setData("Text", text);
                    }
                    e.preventDefault();
                };
            selectElementText(tagsEl[0]);
            document.addEventListener("copy", listener);
            document.execCommand("copy");
            document.removeEventListener("copy", listener);
        };
        writeText(btn);
    }
});