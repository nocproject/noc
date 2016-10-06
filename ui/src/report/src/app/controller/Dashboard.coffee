###
	Управление логикой дашбордов.
    TODO Реордеринг дашбордов.
    TODO При закрытии и удалении показывать прошлый активный, а не первый.
    TODO Кнопка отмены удаления.
###
Ext.define 'Report.controller.Dashboard',
	extend: 'Ext.app.Controller'
	id: 'dashboard'

	###
        @event refresh
		Оповещает о необходимости полностью обновить отчет.
		@param {Report.controller.Dashboard} this Контроллер.
	###

	###
		Оповещает о необходимости добавления виджета.
		@param {Report.controller.Dashboard} this Контроллер.
		@param {Report.view.dashboard.AddWidget} button Кнопка добавления виджета.
	###
	
	listen:
		controller:
			'#root':
				addDashboardAction: 'showDashboardsLibrary'
			'#configurator':
				startSave: 'saveDashboard'
		component:
			'dashboardMain #addWidget':
				click: 'showWidgetLibrary'
			'dashboardMain #configure':
				click: 'configureDashboard'
			'dashboardMain #close':
				click: 'closeDashboard'
			'dashboardLibrary #control #create':
				click: 'createDashboard'
			'dashboardLibrary #control #delete':
				click: 'deleteDashboard'
			'dashboardLibrary #control #select':
				click: 'addDashboardFromLibrary'

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
			@fireEvent 'addDashboardAction', @, button
	
		###
			Запускает редактирование дашборда.
            @param {Ext.button.Button} Кнопка открытия конфигуратора.
		###
		configureDashboard: (button) ->
			Ext.create 'Report.view.dashboard.Configurator',
				entityModel: button.up('dashboardMain').getModel()
	
		###
			Показывает конфигуратор дашборда без начальных данных.
		###
		createDashboard: () ->
			Ext.create 'Report.view.dashboard.Configurator'
	
		###
			Добавляет дашборд из библиотеки дашбордов.
			@param {Ext.button.Button} button Кнопка добавления дашборда.
		###
		addDashboardFromLibrary: (button) ->
			library = button.up('dashboardLibrary')
			list = library.down('#list')
			selected = list.getSelected()
			
			for dashboardData in selected
				@blurActiveDashboard()
				
				dashboardData.set 'active', true
				dashboardData.set 'visible', true
			
			@fireEvent 'refresh', @
				
			library.hide()
	
		###
            Сохраняет дашборд.
            @param {Report.controller.Configurator} controller Контроллер конфигуратора.
            @param {Report.model.configurator.Model} model Модель конфигуратора.
            @param {Ext.data.Model/Null} entityModel Модель сущности, которую конфигурируем, если есть.
		###
		saveDashboard: (controller, model, entityModel) ->
			dashboards = @getDashboards()
			get = model.get.bind model
			
			data = {
				name:        get 'name'
				tags:        get 'tags'
				description: get 'description'
				filters:     get 'filters'
				active:      true
				visible:     false
			}
			
			if entityModel
				data.visible = true
				entityModel.set data
			else
				dashboards.add data
			
			@fireEvent 'refresh', @
	
		###
            Закрывает текущий дашборд.
			@param {Ext.button.Button} button Кнопка закрытия дашборда.
		###
		closeDashboard: (button) ->
			button.up('dashboardMain').getModel().set 'visible', false
			@getDashboards().first()?.set('active', true)
			
			@fireEvent 'refresh', @
	
		###
			Удаляет выбранный дашборд.
			@param {Ext.button.Button} button Кнопка удаления дашборда.
		###
		deleteDashboard: (button) ->
			library = button.up('dashboardLibrary')
			list = library.down('#list')
			selected = list.getSelected()
			dashboards = @getDashboards()
			
			for dashboardData in selected
				dashboards.remove dashboardData
				dashboards.first()?.set('active', true)
				
			@fireEvent 'refresh', @
		
		###
			Убирает флаг активного с текущего активного дашборда.
		###
		blurActiveDashboard: () ->
			@getDashboards().findRecord('active', true)?.set('active', false)
			
		###
            @return {Ext.data.Store} Стор, хранящий существующие дашборды.
		###
		getDashboards: () ->
			Report.model.MainDataTree.get('dashboards')