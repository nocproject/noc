Ext.define 'Report.Viewport',
	extend: 'Ext.container.Viewport'

	layout: 'fit'

	items:
		xtype: 'panel'
		layout: 'fit'
		tbar:
			xtype: 'nocMenu'
		items:
			xtype: 'board'