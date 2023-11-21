/**
 * @class Midoffice.plugin.badgeable.Badgeable
 * Badgeable plugin class used to add a method setBadgeText on any component that uses this plugin.
 * @example
 * // add the plugin in the requires:
 * requires: ['Midoffice.plugin.badgeable.Badgeable']
 *
 * Show the badge in a Panel header:
 * var myPanel = Ext.create('Ext.panel.Panel', {
 *   title: 'Hello',
 *   width: 200,
 *   html: '<p>World!</p>',
 *   plugins: ['badgeable'],
 *   renderTo: Ext.getBody()
 * });
 * myPanel.setBadgeText(3); // by default badgeText is added after the title element of a panel
 *
 * Showing it in a Button, also can be done with bindings
 * var button = Ext.create('Ext.button.Button', {
 *   text: 'Changes',
 *   badgeText: '0',
 *   bind: {
 *     badgeText: '{changesCount}'
 *   },
 *   plugins: ['badgeable']
 * });
 *
 * button.getViewModel().set('changesCount', 33); // would update the badge automatically
 */
Ext.define('Ext.ux.plugin.badgeable.Badgeable', {
    extend: 'Ext.plugin.Abstract',
    alias: 'plugin.badgeable',

    config: {
        /**
         * @cfg {String} badgeText
         * Optional badge text. Badges appear as small numbers, letters, or icons that sit on top of a component.
         */
        badgeText: null,
        /**
         * @cfg {String/Ext.dom.Element/Function} insertAfter
         * Indicates where the badge text should be inserted, don't use it alongside with {@link #insertBefore}, use one or the other
         */
        insertAfter: null,
        /**
         * @cfg {String/Ext.dom.Element/Function} insertBefore
         * Indicates where the badge text should be inserted, don't use it alongside with {@link #insertAfter}, use one or the other
         */
        insertBefore: null,
        /**
         * @private
         * @cfg {String} insertOnParentEvent
         * Indicates upon which event of the parent this component should be rendered
         */
        insertOnParentEvent: 'afterrender',
        /**
         * @cfg {String} cls
         * a class placeholder for the user to enter a desired class to overwrite the styles of this badgeText
         */
        cls: '',
        /**
         * @private
         * @cfg {String} defaultCls
         * Default class of the component
         */
        defaultCls: 'noc-badge',
        /**
         * @cfg {Ext.XTemplate/String/String[]} badgeableRenderTpl
         */
        badgeableRenderTpl: [
            '<span class="{defaultCls} {cls}" style="<tpl if=\'!badgeText || badgeText == "0" \'>display: none;</tpl>{style}" data-qtip="{toolTip}">{badgeText}</span>'
        ],
        /**
         * @cfg {String} toolTip
         * A tooltip text to display when the user hovers the mouse over the badgeText element
         */
        toolTip: null
    },

    init: function(parentCmp) {
        this.callParent(arguments);
        this.cmp.on(this.insertOnParentEvent, this.renderBadgeEl, this);
        if(!this.insertBefore && !this.insertAfter) {
            if(this.cmp instanceof Ext.button.Button) {
                this.insertAfter = 'btnEl';
            } else if(this.cmp instanceof Ext.panel.Panel)
                this.insertAfter = 'header.title.textEl';
            else this.insertAfter = 'el';
        }
        this.cmp.setBadgeText = this.setBadgeText.bind(this);
        this.cmp.setBadgeToolTip = this.setToolTip.bind(this);

        // If the badgeText is configured at the component level
        if(this.cmp.badgeText && !this.badgeText) {
            this.setBadgeText(this.cmp.badgeText)
        }
    },

    destroy: function() {
        if(this.cmp) {
            this.cmp.un(this.insertOnParentEvent, this.renderBadgeEl);
            this.destroyBadgeEl();
        }
        this.callParent(arguments);
    },

    destroyBadgeEl: function() {
        try {
            var badgeEl = Ext.get(this.badgeEl);
            badgeEl && badgeEl.destroy();
            this.badgeEl = null;
            this.cmp && delete this.cmp.badgeEl;
        } catch(err) {
            // could not destroy the badge or it was already destroyed
        }
    },

    renderBadgeEl: function() {
        if(this.badgeEl || (this.cmp && this.cmp.badgeEl)) {
            this.destroyBadgeEl();
        }
        // create the template
        this.badgeTpl = this.badgeTpl || Ext.XTemplate.getTpl(this, 'badgeableRenderTpl');
        // find the element which we want to insert this badge before or after it
        var afterEl = this.getInsertAfter();
        var beforeEl = this.getInsertBefore();

        // rendering the template
        if(afterEl instanceof Ext.dom.Element) {
            this.badgeEl = this.badgeTpl.insertAfter(afterEl, this.getTplData());
        } else if(beforeEl instanceof Ext.dom.Element) {
            this.badgeEl = this.badgeTpl.insertBefore(beforeEl, this.getTplData());
        }

        if(this.cmp) {
            this.cmp.badgeEl = this.badgeEl;
        }
        console.log(this.cmp.updateLayout());
    },

    getInsertAfter: function() {
        return this.insertAfter instanceof Ext.dom.Element ? this.insertAfter : Ext.isFunction(this.insertAfter) ? this.insertAfter.call(this.cmp) : this.get(this.cmp, this.insertAfter);
    },

    getInsertBefore: function() {
        return this.insertBefore instanceof Ext.dom.Element ? this.insertBefore : Ext.isFunction(this.insertBefore) ? this.insertBefore.call(this.cmp) : this.get(this.cmp, this.insertBefore);
    },

    getTplData: function() {
        console.log("getTplData", this.style);
        return {
            cls: this.cls,
            style: this.style,
            defaultCls: this.defaultCls,
            badgeText: this.badgeText,
            toolTip: this.toolTip
        };
    },

    setBadgeText: function() {
        this.callParent(arguments);
        this.renderBadgeEl();
    },

    setToolTip: function() {
        this.callParent(arguments);
        this.renderBadgeEl();
    },
    get: function(obj, path, defaultValue) {
        if(!path) return defaultValue;
        var keys = path.split('.');

        for(let key of keys) {
            if(obj && typeof obj === 'object' && key in obj) {
                obj = obj[key];
            } else {
                return defaultValue;
            }
        }

        return obj;
    }
});