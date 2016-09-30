###
	Управление логикой дашбордов.
###
Ext.define 'Report.controller.Dashboard',
	extend: 'Ext.app.Controller'
	id: 'dashboard'
	
	listen:
		controller:
			'#root':
				addDashboardAction: 'showDashboardsLibrary'
		component:
			'dashboardMain #addWidget':
				click: 'showWidgetLibrary'
			'dashboardMain #configure':
				click: 'configureDashboard'
			'dashboardLibrary #control #create':
				click: 'createDashboard'
			'dashboardLibrary #control #select':
				click: 'addDashboard'

	privates:

		###
			Показывает библиотеку дашбордов.
		###
		showDashboardsLibrary: () ->
			Ext.create('Report.view.dashboard.Library').show()
	
		###
			Показывает библиотеку виджетов.
			@param {Report.view.dashboard.AddWidget} button Кнопка добавления виджета.
		###
		showWidgetLibrary: (button) ->
			
			###
				Оповещает о необходимости добавления виджета.
				@param {Report.controller.Dashboard} this Контроллер.
				@param {Report.view.dashboard.AddWidget} button Кнопка добавления виджета.
			###
			@fireEvent 'addDashboardAction', @, button
	
		###
			Запускает редактирование дашборда.
            @param {Ext.button.Button} Кнопка открытия конфигуратора.
		###
		configureDashboard: (button) ->
			Ext.create 'Report.view.dashboard.Configurator',
				targetEntity: button.up 'dashboardConfigurator'
	
		###
			Показывает конфигуратор дашборда.
		###
		createDashboard: () ->
			Ext.create 'Report.view.dashboard.Configurator'
	
			# TODO
	
		###
			Добавляет дашборд.
			@param {Ext.button.Button} button Кнопка добавления дашборда.
		###
		addDashboard: (button) ->
			list = button.up('dashboardLibrary').down('#list')
			dashboardData = list.getSelected()
			
			unless dashboardData then return
			
			###
				Оповещает о необходимости добавления дашборда.
				@param {Report.controller.Dashboard} this Контроллер.
				@param {Report.model.config.Dashboard} dashboardData Данные дашборда.
			###
			@fireEvent 'addDashboardAction', @, dashboardData