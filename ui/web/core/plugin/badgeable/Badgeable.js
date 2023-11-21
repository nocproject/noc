//---------------------------------------------------------------------
// Badgeable
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.plugin.badgeable.Badgeable");
Ext.define("NOC.core.plugin.badgeable.Badgeable", {
    extend: "Ext.plugin.Abstract",
    alias: "plugin.badgeable",
    insertOnParentEvent: "afterrender",
    cls: "",
    defaultCls: "noc-badge",
    badgeTpl: "<span class='{defaultCls} {cls}' style='<tpl if=\"!badgeText || badgeText == '0' \">display: none;</tpl>'>{badgeText}</span>",
    init: function(parentCmp) {
        this.callParent(arguments);
        this.cmp.on(this.insertOnParentEvent, this.renderBadgeEl, this);
        if(this.cmp instanceof Ext.button.Button) {
            this.insertBadge = "btnEl";
        } else if(this.cmp instanceof Ext.panel.Panel) {
            this.insertBadge = "header.title.textEl";
        }
        else {
            this.insertBadge = "el";
        }
        console.log("insertBadge", this.insertBadge);
        // bind method setBadgeText to parent object
        this.cmp.setBadgeText = this.setBadgeText.bind(this);
        // If the badgeText is configured at the component level
        if(this.cmp.badgeText && !this.badgeText) {
            this.setBadgeText(this.cmp.badgeText)
        }
    },

    destroy: function() {
        console.log('destroy');
        if(this.cmp) {
            this.cmp.un(this.insertOnParentEvent, this.renderBadgeEl);
            this.destroyBadgeEl();
        }
        this.callParent(arguments);
    },
    renderBadgeEl: function() {
        console.log("renderBadgeEl 1:", this);
        if(this.badgeEl || (this.cmp && this.cmp.badgeEl)) {
            this.destroyBadgeEl();
        }
        this.badgeTpl = Ext.XTemplate.getTpl(this, "badgeTpl");
        var afterEl = this.getInsertBadge();
        console.log("afterEl", afterEl);
        // console.log("renderBadgeEl 2: ", this.badgeTpl);
        // console.log(this.cmp.insertBadge, this.cmp.el.insertBadge);
        // this.badgeEl = this.cmp.el.insertBadge(this.badgeTpl.apply(this.getTplData()));
        // console.log(this.badgeEl);
        this.badgeEl = this.badgeTpl.insertAfter(afterEl, this.getTplData());
        if(this.cmp) {
            this.cmp.badgeEl = this.badgeEl;
        }
    },
    destroyBadgeEl: function() {
        try {
            var badgeEl = Ext.get(this.badgeEl);
            console.log('destroy badgeEl', badgeEl);
            badgeEl && badgeEl.destroy();
            this.badgeEl = null;
            this.cmp && delete this.cmp.badgeEl;
        } catch(err) {
            // could not destroy the badge or it was already destroyed
        }
    },
    getTplData: function() {
        return {
            cls: this.cls,
            defaultCls: this.defaultCls,
            badgeText: this.badgeText
        };
    },
    setBadgeText: function() {
        // this.callParent(arguments);
        this.renderBadgeEl();
    },
    getInsertBadge: function() {
        if(this.insertBadge instanceof Ext.dom.Element) {
            return this.insertBadge;
        } else if(Ext.isFunction(this.insertAfter)) {
            return this.insertAfter.call(this.cmp);
        } else {
            return this.get(this.cmp, this.insertBadge);
        }
        // return this.insertBadge instanceof Ext.dom.Element ? this.insertBadge : Ext.isFunction(this.insertBadge) ? this.insertAfter.call(this.cmp) : this.get(this.cmp, this.insertBadge);
    },
    get: function(obj, path, defaultValue) {
        console.log(obj, path, defaultValue);
        if(!path) return defaultValue;
        var keys = path.split('.');

        for(let key of keys) {
            console.log(key);
            if(obj && typeof obj === 'object' && key in obj) {
                console.log("key found");
                obj = obj[key];
            } else {
                console.log("key not found");
                return defaultValue;
            }
        }

        return obj;
    }
});