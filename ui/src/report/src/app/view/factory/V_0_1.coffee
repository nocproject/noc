###
	Фабрика отчетов версии 0.1
	Используюет единую плоскую структуру конфига
	для хранения текущего состояния при конструировании отчета.
###
Ext.define 'Report.view.factory.V_0_1',
	extend: 'Report.view.factory.Abstract'
	
	requires: [
		'Report.view.dashboard.Main'
		'Report.view.root.Main'
		'Report.view.widget.Main'
	]
	
	statics:
		clean: () -> Report.getCmp('rootMain #tabPanel').removeAll(true)
	
	config:
	
		###
			@cfg {Report.view.dashboard.Main} dashboard Текущий дашборд.
		###
		dashboard: null
	
		###
			@cfg {Report.model.config.Dashboard} dashboardModel Текущая модель дашборда.
		###
		dashboardModel: null
	
		###
			@cfg {Report.view.filter.Main} dashboardFilter Текущий фильтр дашборда.
		###
		dashboardFilter: null
	
		###
			@cfg {Report.model.config.Filter} dashboardFilterModel Текущая модель фильтра дашборда.
		###
		dashboardFilterModel: null
	
		###
			@cfg {Report.view.widget.Main} widget Текущий виджет.
		###
		widget: null
	
		###
			@cfg {Report.model.config.Widget} widgetModel Текущая модель виджета.
		###
		widgetModel: null
	
		###
			@cfg {Report.view.filter.Main} widgetFilter Текущий фильтр виджета.
		###
		widgetFilter: null
	
		###
			@cfg {Report.model.config.Filter} widgetFilterModel Текущая модель виджета фильтра.
		###
		widgetFilterModel: null
	
		###
			@cfg {Ext.data.Store} columnsStore
			Текущие хранилище колонок виджета на основе модели Report.model.config.Filter.
		###
		columnsStore: null

	###
		Создает отчет по входящей модели.
		@param {Ext.data.Model} model Модель отчета.
	###
	make: (model) ->
		model.get('dashboards')?.each (dashboard) =>
			@setDashboardModel dashboard
			
			@makeDashboard()
			
			return unless @getDashboard()
			
			dashboard.get('widgets')?.each (widget) =>
				@setWidgetModel widget
				@setColumnsStore widget.get 'columns'
				
				@makeWidget()
					
	privates:
	
		###
			Создание дашборда.
		###
		makeDashboard: () ->
			model = @getDashboardModel()
			tabPanel = Report.getCmp('rootMain #tabPanel')
			
			unless model.get 'visible'
				@setDashboard null
				return
				
			dashboard = Ext.create {
				xtype: 'dashboardMain'
				model: model
				title: model.get 'name'
			}
			
			@setDashboard dashboard

			tabPanel.add dashboard
			
			if model.get 'active'
				tabPanel.setActiveTab dashboard
		
		###
			Создание виджета.
		###
		makeWidget: () ->
			model = @getWidgetModel()
			
			return unless model.get 'visible'
			
			target = @getDashboard().down('#widgets')
			columns = @getColumnsStore()
			widget = Ext.create {
				xtype: 'widgetMain'
				model: model
				columns: columns
				title: model.get 'name'
			}
			
			target.add widget