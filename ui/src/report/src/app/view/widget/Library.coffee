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
	
	listeners:
		afterrender: () ->
			dashboards = Report.model.MainDataTree.get('dashboards')
			widgets = dashboards.findRecord('active', true)?.get('widgets')
			
			return unless widgets
			
			list = @down('#list')
			
			widgets.on 'add', list.selectNew.bind list
			
			list.setStore widgets