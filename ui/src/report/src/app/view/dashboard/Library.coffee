###
    Библиотека дашбордов.
###
Ext.define 'Report.view.dashboard.Library',
	extend: 'Report.view.library.Main'
	xtype: 'dashboardLibrary'
	
	title: 'Бибилиотека дашбордов'
	
	store: {
		model: 'Report.model.config.Dashboard'
		proxy: 'memory'
	}