//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.monitor.Application');
Ext.define('NOC.sa.monitor.Application', {
    extend: 'NOC.core.Application',
    requires: [
        'NOC.sa.monitor.Controller',
        'NOC.sa.monitor.ViewModel',
        'NOC.core.filter.Filter',
        'NOC.sa.monitor.SelectionGrid'
    ],

    alias: 'widget.monitor',

    layout: 'border',
    controller: 'monitor',
    viewModel: 'monitor',
    border: false,
    stateful: true,
    stateId: 'monitor.appPanel',

    items: [
        {
            xtype: 'selectionGrid',
            region: 'west',
            resizable: true,
            split: true,
            width: '80%'
        },

        {
            xtype: 'NOC.Filter',
            // appId: this.appId,
            appId: 'sa.monitor',
            reference: 'filterPanel',
            region: 'east',
            width: 300,
            collapsed: true,
            border: true,
            animCollapse: false,
            collapseMode: 'mini',
            hideCollapseTool: true,
            split: true,
            resizable: true,
            stateful: true,
            stateId: 'monitor.filterPanel',
            selectionStore: 'monitor.objectsStore',
            treeAlign: 'right'
        }
    ]
});