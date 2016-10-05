###
	Библиотека дашбордов.
###
Ext.define 'Report.view.dashboard.Library',
	extend: 'Report.view.library.Main'
	xtype: 'dashboardLibrary'
	
	title: 'Библиотека дашбордов'
	
	store: {
		model: 'Report.model.config.Dashboard'
		proxy: 'memory'
	}
	
	listeners:
		afterrender: () ->
			dashboards = Report.model.MainDataTree.get('dashboards')
			list = @down('#list')
			
			dashboards.on 'add', list.selectNew.bind list
			
			list.setStore dashboards