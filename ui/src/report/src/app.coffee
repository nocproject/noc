Ext.application(
	extend: 'Ext.app.Application'
	name: 'Report'
	
	requires: [
		'Report.view.root.Main'
		'Report.model.MainDataTree'
		'Report.factory.V_0_1'
	]
	
	controllers: [
		'Root'
		'Configurator'
		'Dashboard'
		'Library'
		'Widget'
	]
	
	mainView: 'Report.view.root.Main'
	
	constructor: () ->
		Report.getAllCmp = (query) -> Ext.ComponentQuery.query(query)
		Report.getCmp    = (query) -> Ext.ComponentQuery.query(query)[0]
			
		@callParent arguments
	
	launch: () ->
		@showLoader()
		@makeReport()
		
	privates:
		
		###
            Отображает прелоадер.
		###
		showLoader: () ->
			body = Ext.getBody()
	
			loader = Ext.create 'Ext.Img',
				floating: true,
				src: 'resources/img/SOVA.png',
				alt: 'SOVA logo'
				autoShow: true,
				shadow: false,
				x: body.getWidth() / 2 - 380,
				y: body.getHeight() / 2 - 88
			
			loader.animate {
				delay: 1000
				duration: 1200
				to:
					opacity: 0
			}
			
			setTimeout(
				() -> loader.destroy()
				2500
			)

		###
            Создает-инициализирует отчет.
		###
		makeReport: () ->
			@controllers.getAt(0).makeReport()
)