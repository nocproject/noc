###
	Библиотека виджетов.
###
Ext.define 'Report.view.widget.Library',
	extend: 'Report.view.library.Main'
	xtype: 'widgetLibrary'
	
	title: 'Библиотека виджетов'
	
	store: {
		model: 'Report.model.config.Widget'
		proxy: 'memory'
	}