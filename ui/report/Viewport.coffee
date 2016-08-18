Ext.define 'Report.Viewport',
	extend: 'Ext.container.Viewport'
	requires: [
		'Report.NocMenu'
	]

	items:
		xtype: 'panel'
		layout: 'fit'
		tbar:
			xtype: 'nocMenu'
		items:
			xtype: 'board'