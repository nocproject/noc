###
	Управление логикой конфигуратора.
###
Ext.define 'Report.controller.Configurator',
	extend: 'Ext.app.Controller'
	id: 'configurator'
	
	requires: [
		'Report.model.configurator.Model'
	]
	
	listen:
		component:
			'configuratorMain configuratorControl #save':
				click: 'saveData'
	
	###
        Сохраняет введенные данные.
        @param {Ext.button.Button} button Кнопка сохранения.
	###
	saveData: (button) ->
		configurator = button.up('configuratorMain')
		get = @getValueGetter configurator
		model = Ext.create 'Report.model.configurator.Model'
		
		model.set {
			type:        get('#type #combo')
			name:        get('#meta #name')
			tags:        get('#meta #tags')
			description: get('#meta #description')
			width:       get('#size #width')
			height:      get('#size #height')
			point:       get('#wellspring #combo')
			columns:     get('#wellspring #grid')
			filters:     get('#filters #grid')
		}
		
		###
            Оповещает о начале сохранения данных конфигуратора.
            @param {Report.controller.Configurator} this Конфигуратор.
            @param {Report.model.configurator.Model} model Модель.
        ###
		@fireEvent 'startSave', @, model
		
	privates:
		
		###
            Конструирует геттер, который принимает селектор
            и возвращает значение поля. Если полем является компонент,
            не являющийся полем - возвращается массив данных стора компонента в виде объетов.
            @param {Ext.Component} component Компонент.
            @return {Mixed} Значение.
		###
		getValueGetter: (component) -> (selector) =>
			target = component.down(selector)
			
			if target instanceof Ext.form.field.Base
				target.getValue()
			else
				data = target.getStore().getData()
				
				Ext.Array.from(data).map (value) -> value.getData()