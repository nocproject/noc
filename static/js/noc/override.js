//
// ExtJS overrides
//

/*
 * Purpose: to make text selectable in a Ext JS 4 grid
 *
 * Usage for MVC app:
 * 
 * 1. copy this file to feature/selectable.js
 * 2. add this to your grid config:
 
    features: [
        {ftype: 'selectable', id: 'selectable'}
    ],
 
 * Tested with Ext.grid.Panel in Ext JS 4.0.2a MVC app
 */
 
Ext.require('Ext.view.Table', function() {
    Ext.override(Ext.view.Table, {
        afterRender: function() {
            var me = this;
 
            me.callParent();
            me.mon(me.el, {
                scroll: me.fireBodyScroll,
                scope: me
            });
 
            // in case the selectable feature is present, don't do me.el.unselectable() 
            if ( me.getFeature('selectable')===undefined ) {
                me.el.unselectable();
            }
            me.attachEventsForFeatures();
        }
    });
});
 
Ext.require('Ext.grid.feature.Feature', function() {
    Ext.define('feature.selectable', {
        extend: 'Ext.grid.feature.Feature',
        alias: 'feature.selectable',
 
        mutateMetaRowTpl: function(metaRowTpl) {
            var i,
                ln = metaRowTpl.length;
 
            for (i = 0; i < ln; i++) {
                tpl = metaRowTpl[i];
                tpl = tpl.replace(/x-grid-row/, 'x-grid-row x-selectable');
                tpl = tpl.replace(/x-grid-cell-inner x-unselectable/g, 'x-grid-cell-inner');
                tpl = tpl.replace(/unselectable="on"/g, '');
                metaRowTpl[i] = tpl;
            }
        }        
    });
});
