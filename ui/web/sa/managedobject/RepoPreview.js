//---------------------------------------------------------------------
// NOC.sa.managedobject.RepoPreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.RepoPreview");

Ext.define("NOC.sa.managedobject.RepoPreview", {
    extend: "NOC.core.RepoPreview",
    initComponent: function() {
        var me = this, toolbarItems, index;
        me.menuBtn = Ext.create("Ext.button.Split", {
            itemId: "menuBtn",
            text: "Compare By",
            menu: [
                {
                    text: __("Version"),
                    handler: Ext.pass(me.menuBtnFn, "version", me)
                },
                {
                    text: __("Other Object"),
                    handler: Ext.pass(me.menuBtnFn, "object", me)
                // },
                // {
                //     xtype: "checkbox",
                //     boxLabel: __("Side-By-Side"),
                //     boxLabelAlign: "before",
                //     fieldCls: Ext.baseCSSPrefix + "menu-item",
                //     // fieldCls: "",
                //     formItemCls: Ext.baseCSSPrefix + "menu-item-default"
                }
            ]
        });
        me.objectCombo = Ext.create("NOC.sa.managedobject.LookupField", {
            itemId: "objectCombo",
            fieldLabel: __("Object"),
            labelPad: 5,
            labelWidth: undefined,
            labelCls: Ext.baseCSSPrefix + "form-item-label " + Ext.baseCSSPrefix + "form-item-label-toolbar",
            hidden: true,
            listeners: {
                scope: me,
                select: me.onSelectObject,
                clear: me.onClearObject
            }
        });
        me.callParent();
        toolbarItems = me.dockedItems.items[0].items;
        index = toolbarItems.indexOfKey("swapRevBtn");
        toolbarItems.insert(index, me.menuBtn);
        toolbarItems.insert(index + 3, me.objectCombo);
        me.diffCombo.setFieldLabel(__("Version"));
        me.swapRevButton.hide();
        me.diffCombo.hide();
        me.prevDiffButton.hide();
        me.nextDiffButton.hide();
        // me.sideBySideModeButton.hide();
        me.diffCombo.un("select", me.onSelectDiff, me);
        me.diffCombo.on("select", me.localListener(me.onSelectDiff), me);
        me.sideBySideModeButton.setHandler(me.localListener(me.onSideBySide), me);
        me.resetButton.handler = function() {
            me.clearHideCombo(me.diffCombo);
            me.clearHideCombo(me.objectCombo);
            this.requestText();
            this.requestRevisions();
        }
    },
    menuBtnFn: function(type) {
        var me = this;
        me.compareType = type;
        switch(type) {
            case "object": {
                me.clearHideCombo(me.diffCombo);
                me.objectCombo.show();
                break;
            }
            case "version": {
                me.clearHideCombo(me.objectCombo);
                me.diffCombo.setValue(null);
                me.requestRevisions();
                me.diffCombo.show();
                break;
            }
        }
    },
    onSelectObject: function(combo, record) {
        var me = this;
        me.requestRevisions(record.id);
        me.diffCombo.show();
    },
    onClearObject: function() {
        var me = this;
        me.clearHideCombo(me.diffCombo);
    },
    clearHideCombo: function(combo) {
        combo.setValue(null);
        combo.store.loadData([]);
        combo.hide();
    },
    localListener: function(listener) {
        var me = this, rev1, rev2, objectId;
        return function() {
            if(me.compareType === "version") {
                listener.call(me);
            } else if(me.compareType === "object") {
                rev1 = me.revCombo.getValue();
                rev2 = me.diffCombo.getValue();
                objectId = me.objectCombo.getValue();
                me.requestDiff(rev1, rev2, objectId);
            }
        }
    }
});
