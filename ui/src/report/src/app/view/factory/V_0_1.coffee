###
    Фабрика отчетов версии 0.1
    Используюет единую плоскую структуру конфига
    для хранения текущего состояния при конструировании отчета.
###
Ext.define 'Report.factory.V_0_1',
	extend: 'Report.factory.Abstract'
	
	requires: [
		'Report.view.dashboard.Main'
		'Report.view.filter.Factory'
		'Report.view.root.Main'
		'Report.view.widget.Main'
	]
	
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
		model.get('dashboards').each (dashboard) ->
			@setDashboardModel dashboard
			
			@makeDashboard()
			
			dashboard.get('filters').each (filter) ->
				@setDashboardFilterModel filter
				
				@makeDashboardFilter()
				
			dashboard.get('widgets').each (widget) ->
				@setWidgetModel widget
				@setColumnsStore widget.get 'columns'
				
				@makeWidget()
				
				widget.get('filters').each (filter) ->
					@setWidgetFilterModel filter
					
					@makeWidgetFilter()
					
	privates:
	
		###
            Создание дашборда.
		###
		makeDashboard: () ->
			model = @getDashboardModel()
			tabPanel = Ext.ComponentQuery.query('rootMain #tabPanel')
			dashboard = Ext.create {
				xtype: 'dashboardMain'
				model: model
				title: model.get 'name'
			}
			
			@setDashboard dashboard
			tabPanel.add dashboard
			
		###
            Создание фильтра для дашборда.
		###
		makeDashboardFilter: () ->
			@makeFilter @getDashboardFilterModel(), @getDashboard()
		
		###
            Создание виджета.
		###
		makeWidget: () ->
			model = @getWidgetModel()
			target = @getDashboard().down('#widgets')
			columns = @getColumnsStore()
			widget = Ext.create {
				xtype: 'widgetMain'
				model: model
				columns: columns
			}
			
			target.add widget
		
		###
            Создание фильтра для виджета.
		###
		makeWidgetFilter: () ->
			@makeFilter @getWidgetFilterModel(), @getWidget()
	
		###
			Создание фильтра для виджета.
            @param {Ext.data.Model} model Модель фильтра.
            @param {Ext.Container} container Контейнер, содержащий область с id '#filters'
		###
		makeFilter: (model, container) ->
			target = container.down('#filters')
			filterWidgets = Report.view.filter.Factory.makeFilter(model)
			
			target.add.apply target, filterWidgets