//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.monitor.Controller');
Ext.define('NOC.sa.monitor.Controller', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.monitor',

    mixins: [
        'NOC.core.Export'
    ],

    onShowFilter: function() {
        this.lookupReference('filterPanel').toggleCollapse();
    },

    onReload: function() {
        this.getViewModel().getStore('objectsStore').reload();
    },

    onSelectionChange: function(element, selected) {
        this.getViewModel().set('total.selection', selected.length);
    },

    onSelectAll: function() {
        var selectionGrid = this.lookupReference('selectionGrid');
        var renderPlugin = selectionGrid.findPlugin('bufferedrenderer');

        selectionGrid.getSelectionModel().selectRange(0, renderPlugin.getLastVisibleRowIndex());
    },

    onUnselectAll: function() {
        this.lookupReference('selectionGrid').getSelectionModel().deselectAll();
    },

    onRowDblClick: function(grid, record) {
        this.lookupReference('repoPreview').preview(record);
    },



    onRenderStatus: function(value) {
        var stateCodeToName = {
            W: 'Wait',
            R: 'Run',
            S: 'Stop',
            F: 'Fail',
            D: 'Disabled'
        };

        return (stateCodeToName[value]) ? stateCodeToName[value] : value;
    },

    onRenderTooltip: function(value, metaData) {
        metaData.tdAttr = 'data-qtip="' + value + '"';

        return value;
    },

    onExport: function() {
        this.save(this.lookupReference('selectionGrid'), 'monitor.csv');
    }
});
