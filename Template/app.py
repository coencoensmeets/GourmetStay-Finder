import dash
from dash import dcc, html, ctx
import dash_loading_spinners as dls
from def_class.menu import make_menu_layout, range_slider
import def_class.Middle as Map
from def_class.Output import make_output_layout
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
import numpy as np
import plotly.express as px
import json


# Remove pandas warnings and surpresses DASH GET and POST outputs
import warnings
warnings.filterwarnings("ignore")
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


#Saving data throughout the main interactions of the program. 
class Save_data():
	def __init__(self):
		self.hoverData = [] #Hover data (mouse of item)
		self.clickData=[]
		self.n_clicked = 0 #The amount of times the switch button has been clicked
		self.n_clicked_ctrl = 0 #The amount of times the advanced control button has been clicked
		self.feature = {} #Last feature that was hovered over

	def update_hover(self, data): #Updates the hover data
		self.hoverData = data

	def update_click(self,data): #Updates Clicked data
		self.clickData = data

	def update_clicked(self, n=1): #Updates the click counter for switching maps
		self.n_clicked +=n

	def update_clicked_ctrl(self, n=1): #Updates the click counter for switching advanced controls
		self.n_clicked_ctrl +=n

	def update_click_feature(self, feature):#Updates the last feature that was hovered over
		print("Updated: {}".format(feature))
		self.feature = feature

if __name__ == '__main__':
	print("Loading entire back-end system\n---This can take a few seconds")
	#---Main Setup---
	app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
	app.title = "Group 44"
	Map_data = Map.Map()

	Data_saved = Save_data() #Setup for the storing of data class 
	
	#Layout creation
	app.layout = html.Div(children=[
		html.Div(
			id="div-loading",
			style={'display': 'inline-block', 'position': 'absolute', 'z-index': '10001'},
			children=[
				dls.Bars(
					fullscreen=True, 
					id="loading-whole-app"
				)
			]
		),
		html.Div(
		id="app-container", 
		style={'max-height': '100%'},
		children=[
		#Hidden DIV for OUTPUT Callback
			html.Div(id='hidden-div', style={'display':'none'}),
			html.Div(id='hidden-div2', style={'display':'none'}),
			# Left column
			html.Div(

				id="left-column",
				className="two columns",
				children=make_menu_layout(Map_data)
			),
			# Middle column
			html.Div(
				id="middle-column",
				className="eight columns",
				children=Map_data.html_div
			),
			html.Div(

				id="right-column",
				className="two columns",
				children=make_output_layout()
			),
		],
	)]
	)

#------INTERACTIONS-------
	#-Switch between restaurants and airbnbs & Number of airbnbs+minimap---
	@app.callback([
		Output(component_id ='map', component_property='children'),#Main map component
		Output('btn-switch', 'children'),#Text of the button (Restaurant/airbnb)
		Output('btn-switch', 'style'),#Style of the button (White/dark)
		Output('impr_map', 'style'),#Style of the button (White/dark)
		Output('data_showing', 'children'),#"Currently showing ... map" text
		Output('mini-map', 'children'),#Minimap component
		Output('Nairbnb', 'children'), #Amount of airbnbs text
		Output('meanprice','children'),
		Output('meanservice','children'),
		Output('loading-output', 'value'),
		Output('map_div', 'style'),  #Style of the map div
		Output('adv_ctrl_div', 'style'),
		Output('adv_ctrl_div', 'children'),
		Output("div-loading", "children")
		],
		[
		Input('btn-switch', 'n_clicks'),#The switch from map button input (amount of clicks)
		Input('map', 'bounds'),#The bounds of the map input (Bounds)
		Input('res_filter_graph', 'relayoutData'),
		Input('air_filter_graph', 'relayoutData'),
		Input('btn-controls', 'n_clicks'),
		Input('pcp_id', 'restyleData'),
		Input('cat_air_checklist', 'value'),
		Input('cat_air_drop', 'value'),
		Input('air_reset_button', 'n_clicks'),
		Input('cat_res_checklist', 'value'),
		Input('cat_res_drop', 'value'),
		Input('res_reset_button', 'n_clicks'),
		Input('density_map', 'bounds')
		],
		[
		State(component_id ='map', component_property='children'),
		State('btn-switch', 'children'),
		State('btn-switch', 'style'),
		State('mini-map', 'children'),
		State('Nairbnb', 'children'),
		State('res_filter_drop', 'value'),
		State('air_filter_drop', 'value'),
		State('adv_ctrl_div', 'children')]
		)
	def update_map(N, bounds,layout_graph_res,layout_graph_air, N_adv, pcp_data, 
					cat_air_chosen, cat_air,reset_air, cat_res_chosen, cat_res, reset_res, bounds_density,
					Map_data_list, output_btn, style, Mini, N_airbnb, res_filt_res, res_filt_air, adv_ctrl_div):
		mean_price=""
		mean_service=""
		cur_show = None
		id_input = ctx.triggered_id
		if (id_input=='btn-switch'):
			if N!= Data_saved.n_clicked and N!=0:#Checks whether the button has been clicked and not the loading of the page
				print("Switch")
				Map_data_list = Map_data.switch()#Get the new html data for the new map
				Data_saved.update_clicked()#Update the saved click counter

				if Map_data.Show =='Restaurants':#If the restaurants are shown
					output_btn = "Show AirBnBs"
					style = {'border-color':'black','color':'black'}#Change the colour of the button to be visible on the background
				else:#Checks whether Airbnbs are shown
					output_btn = "Show Restaurants"
					style = {'border-color':'white',
						'color':'white'}#change colour of button to be visible on background
				Count = Map.N_airbnbs(Map_data,bounds) #Calculates amount of airbnbs in shown region
				Mini = Map_data.update_bounds_mini(bounds) #With the bounds update the minimap (Output is html data for the minimap)
				N_airbnb = "Number of AirBnBs: {}".format(Count[0])
				mean_price = "Average Price of an AirBnB: ${}".format(Count[1])
				mean_service = "Average Service Fee for an AirBnb: ${}".format(Count[2])
				print(N_airbnb)
		if (id_input=='map'):
			Mini = Map_data.update_bounds_mini(bounds) #With the bounds update the minimap (Output is html data for the minimap)
			Count = Map.N_airbnbs(Map_data,bounds) #Calculates amount of airbnbs in shown region
			N_airbnb = "Number of AirBnBs: {}".format(Count[0])
			mean_price = "Average Price: ${}".format(Count[1])
			mean_service = "Average Service Fee: ${}".format(Count[2])


		#Change of filter (Restaurants)
		if (id_input == 'res_filter_graph') and ('xaxis.range' in layout_graph_res.keys()):
			print("Restaurant filter UPDATE")
			Map_data.Filter_class.update_res(res_filt_res, layout_graph_res['xaxis.range']) #Update the filtering class
			Count = Map.N_airbnbs(Map_data,bounds) #Calculates amount of airbnbs in shown region
			N_airbnb = "Number of AirBnBs: {}".format(Count[0])
			mean_price = "Average Price: ${}".format(Count[1])
			mean_service = "Average Service Fee: ${}".format(Count[2])
			Map_data_list = Map_data.update()

		#Change of filter (Airbnb)
		if (id_input == 'air_filter_graph') and ('xaxis.range' in layout_graph_air.keys()):
			print("Airbnb filter UPDATE")
			Map_data.Filter_class.update_air(res_filt_air, layout_graph_air['xaxis.range'])
			Count = Map.N_airbnbs(Map_data,bounds) #Calculates amount of airbnbs in shown region
			N_airbnb = "Number of AirBnbs: {}".format(Count[0])
			mean_price = "Average Price: ${}".format(Count[1])
			mean_service = "Average Service Fee: ${}".format(Count[2])
			Map_data_list = Map_data.update()
			if Data_saved.n_clicked_ctrl%2 == 1:
				print(bounds_density)
				adv_ctrl_div = Map_data.get_adv_graphs()

		if id_input == 'cat_air_checklist':
			print("Categorical Airbnb UPDATE")
			Map_data.Filter_class.update_cat_air(cat_air,cat_air_chosen)
			Count = Map.N_airbnbs(Map_data,bounds) #Calculates amount of airbnbs in shown region
			N_airbnb = "Number of AirBnBs: {}".format(Count[0])
			mean_price = "Average Price: ${}".format(Count[1])
			mean_service = "Average Service Fee: ${}".format(Count[2])
			Map_data_list = Map_data.update()
			if Data_saved.n_clicked_ctrl%2 == 1:
				adv_ctrl_div = Map_data.get_adv_graphs()
		#Reset of categorical filter (AirBnb)
		if id_input == 'air_reset_button':
			print("Reset Categorical AIRBNB")
			Map_data.Filter_class.update_cat_air(None,None)
			Count = Map.N_airbnbs(Map_data,bounds) #Calculates amount of airbnbs in shown region
			N_airbnb = "Number of AirBnBs: {}".format(Count[0])
			mean_price = "Average Price: ${}".format(Count[1])
			mean_service = "Average Service Fee: ${}".format(Count[2])
			Map_data_list = Map_data.update()
			if Data_saved.n_clicked_ctrl%2 == 1:
				adv_ctrl_div = Map_data.get_adv_graphs()

		if id_input == 'cat_res_checklist':
			print("Categorical RESTAURANT UPDATE")
			Map_data.Filter_class.update_cat_res(cat_res,cat_res_chosen)
			Count = Map.N_airbnbs(Map_data,bounds) #Calculates amount of airbnbs in shown region
			N_airbnb = "Number of AirBnBs: {}".format(Count[0])
			mean_price = "Average Price: ${}".format(Count[1])
			mean_service = "Average Service Fee: ${}".format(Count[2])
			Map_data_list = Map_data.update()
		#Reset of categorical filter (AirBnb)
		if id_input == 'res_reset_button':
			print("Reset Categorical RESTAURANTS")
			Map_data.Filter_class.update_cat_res(None,None)
			Count = Map.N_airbnbs(Map_data,bounds) #Calculates amount of airbnbs in shown region
			N_airbnb = "Number of AirBnBs: {}".format(Count[0])
			mean_price = "Average Price: ${}".format(Count[1])
			mean_service = "Average Service Fee: ${}".format(Count[2])
			Map_data_list = Map_data.update()

		if (id_input=='pcp_id'):
			if pcp_data!=None:
				Data_key = list(pcp_data[0].keys())
				if 'constraintrange' in Data_key[0]:
					Index_column = int(Data_key[0].split('[')[1].split("]")[0])
					Column = Map_data.Filter_class.air_columns[Index_column]
					Range =  list(pcp_data[0].items())[0][1][0]
					print("Update ({}): {}".format(Column, Range))
					Map_data.Filter_class.update_air(Column, Range)
					Count = Map.N_airbnbs(Map_data,bounds) #Calculates amount of airbnbs in shown region
					N_airbnb = "Number of AirBnBs: {}".format(Count[0])
					mean_price = "Average Price: ${}".format(Count[1])
					mean_service = "Average Service Fee: ${}".format(Count[2])

		#Switch to advanced and back.
		if (id_input == 'btn-controls'):
			if N_adv!= Data_saved.n_clicked_ctrl and N_adv!=0:#Checks whether the button has been clicked and not the loading of the page
				print("Clicked")
				Data_saved.update_clicked_ctrl()#Update the click counter
			else:
				print("Not clicked")

		if (id_input== 'density_map'):
			print(bounds_density)

		if Data_saved.n_clicked_ctrl%2 == 0: #Map is shown
			Map_data_list = Map_data.update()
			Output_style_adv = [{'display': 'block'}, {'display': 'none'}]

		else: #Advanced controls will be shown
			cur_show = "Advanced controls (Airbnbs)"
			Output_style_adv = [{'display': 'none'}, {'display': 'block'}]
			adv_ctrl_div = Map_data.get_adv_graphs()

		if cur_show == None:
			cur_show = Map_data.Show

		return Map_data_list, output_btn, style, style,cur_show, Mini, N_airbnb,mean_price,mean_service, "", Output_style_adv[0], Output_style_adv[1], adv_ctrl_div, None

	@app.callback([Output("Information_hover", "children"), #Information div on hover feature
				   Output('Information_click', 'children'), #Information div on click feature
				   Output('tooltip', 'children')], #Tooltop (hovering extension)
				  [Input("markers", "hover_feature"), #Input when a feature is hovered over
		 		   Input("markers", "click_feature")]) #Input when a feature is clicked on
	def update_tooltip(hover_feature,click_feature):
		
		if hover_feature is None and click_feature is None:
			return 'Hover over data to see its information', 'Click on data to save for comparison', None  # return last information and no tooltip
		elif hover_feature == click_feature:
			return Data_saved.hoverData, Data_saved.clickData, Data_saved.clickData[0:4]
		if click_feature is None or (click_feature != hover_feature and hover_feature is not None):
			if hover_feature['properties']['cluster'] == True:  # Check whether the feature is a cluster
				return 'Hover over data to see its information', 'Click on data to save for comparison', [
					html.P('#N={}'.format(hover_feature['properties']['point_count']))]  # Returns cluster information
			elif Map_data.Show == 'Restaurants':  # Restaurant map is shown
				# Creates the html for the information
				Output = [
					html.B("NOT SELECTED"),
					html.P("Name: {}".format(str(hover_feature['properties']['DBA']).lower())),
					html.P("Score: {}".format(hover_feature['properties']['SCORE'])),
					html.P("Cuisine: {}".format(hover_feature['properties']['CUISINE'])),
					html.P("Borough: {}".format(hover_feature['properties']['BOROUGH'])),
					html.P("Violations: {}".format(hover_feature['properties']['VIOLATIONS'])),
					html.P("Violation Criticality: {}".format(hover_feature['properties']['VIOLATION CRITICALITY'])),
					html.P("Grade: {}".format(hover_feature['properties']['GRADE'])),
					html.A(href="https://www.google.com/search?q={} {} {} NYC".format(
						hover_feature['properties']['DBA'],
						hover_feature['properties']['BUILDING'],
						hover_feature['properties']['STREET']).lower()
						   , children=[
							html.Button("Google")
						])]
				# print(feature)
				Data_saved.update_hover(Output)  # update last hover feature
				if click_feature is None:
					return Data_saved.hoverData, 'Click on data to save for comparison', Data_saved.hoverData[0:4]
				else:
					return Data_saved.hoverData, Data_saved.clickData, Data_saved.hoverData[0:4]
			else:  # Airbnb map is shown
				# Creates the html for the information
				Output = [
					html.B("NOT SELECTED"),
					html.P("Name: {}".format(str(hover_feature['properties']['NAME']).lower())),
					html.P("Price: ${}".format(hover_feature['properties']['PRICE'])),
					html.P("Rating: {}".format(hover_feature['properties']['review_rate_number'])),
					html.P("Service Fee: ${}".format(hover_feature['properties']['SERVICE FEE'])),
					html.P("Minimum Nights: {}".format(hover_feature['properties']['MINIMUM NIGHTS'])),
					html.P("Construction Year: {}".format(hover_feature['properties']['CONSTRUCTION YEAR'])),
					html.P("Borough: {}".format(hover_feature['properties']['BOROUGH'])),
					html.P("Number of Reviews: {}".format(hover_feature['properties']['NUMBER OF REVIEWS'])),
					html.P("Number of Host Listings: {}".format(hover_feature['properties']['NUMBER OF HOST LISTINGS'])),
					html.P("Host Identity: {}".format(hover_feature['properties']['HOST IDENTITY'])),
					html.P("Cancellation Policy: {}".format(hover_feature['properties']['CANCELLATION POLICY'])),
					html.P("Instantly Bookable: {}".format(hover_feature['properties']['INSTANTLY BOOKABLE'])),
					html.P("Room Type: {}".format(hover_feature['properties']['ROOM TYPE']))
				]
				Data_saved.update_hover(Output)  # Updates last hover feature
				if click_feature is None:
					return Data_saved.hoverData, 'Click on data to save for comparison', Data_saved.hoverData[0:4]
				else:
					return Data_saved.hoverData, Data_saved.clickData, Data_saved.hoverData[0:4]
		else:
			if click_feature['properties']['cluster'] == True:  # Check whether the feature is a cluster
				return Data_saved.hoverData, Data_saved.clickData, [
					html.P('#N={}'.format(click_feature['properties']['point_count']))]  # Returns cluster information
			elif Map_data.Show == 'Restaurants':  # Restaurant map is shown
				# Creates the html for the information
				Output = [
					html.B("SELECTED"),
					html.P("Name: {}".format(str(click_feature['properties']['DBA']).lower())),
					html.P("Score: {}".format(click_feature['properties']['SCORE'])),
					html.P("Cuisine: {}".format(click_feature['properties']['CUISINE'])),
					html.P("Borough: {}".format(click_feature['properties']['BOROUGH'])),
					html.P("Violations: {}".format(click_feature['properties']['VIOLATIONS'])),
					html.P("Violation Criticality: {}".format(click_feature['properties']['VIOLATION CRITICALITY'])),
					html.P("Grade: {}".format(click_feature['properties']['GRADE'])),
					html.A(href="https://www.google.com/search?q={} {} {} NYC".format(
						click_feature['properties']['DBA'],
						click_feature['properties']['BUILDING'],
						click_feature['properties']['STREET']).lower()
						   , children=[
							html.Button("Google")
						])]
				# print(feature)
				Data_saved.update_click(Output)  # update last click feature
				return Data_saved.hoverData, Data_saved.clickData, Data_saved.hoverData[0:4]
			else:  # Airbnb map is shown
				# Creates the html for the information
				Output = [
					html.B("SELECTED"),
					html.P("Name: {}".format(str(click_feature['properties']['NAME']).lower())),
					html.P("Price: ${}".format(click_feature['properties']['PRICE'])),
					html.P("Rating: {}".format(click_feature['properties']['review_rate_number'])),
					html.P("Service Fee: ${}".format(click_feature['properties']['SERVICE FEE'])),
					html.P("Minimum Nights: {}".format(click_feature['properties']['MINIMUM NIGHTS'])),
					html.P("Construction Year: {}".format(click_feature['properties']['CONSTRUCTION YEAR'])),
					html.P("Borough: {}".format(click_feature['properties']['BOROUGH'])),
					html.P("Number of Reviews: {}".format(click_feature['properties']['NUMBER OF REVIEWS'])),
					html.P("Number of Host Listings: {}".format(click_feature['properties']['NUMBER OF HOST LISTINGS'])),
					html.P("Host Identity: {}".format(click_feature['properties']['HOST IDENTITY'])),
					html.P("Cancellation Policy: {}".format(click_feature['properties']['CANCELLATION POLICY'])),
					html.P("Instantly Bookable: {}".format(click_feature['properties']['INSTANTLY BOOKABLE'])),
					html.P("Room Type: {}".format(click_feature['properties']['ROOM TYPE']))
				]
				Data_saved.update_click(Output)  # Updates last click feature
				return Data_saved.hoverData, Data_saved.clickData, Data_saved.hoverData[0:4]

	#Update the feature clicked in data stored
	@app.callback(Output('hidden-div', 'children'),#Output hidden div as no information has to be passed with this input
		Input('markers', 'click_feature'))#If a feature has been clicked
	def get_clicked_marker(feature):
		if feature== None:#Check if page is loaded
			pass
		elif feature['properties']['cluster'] ==True:#Checks if 
			pass
		elif Map_data.Show!="Restaurants":#If the airbnbs are shown
			Data_saved.update_click_feature(feature)#Update the feature clicked
		return None

	# Switch from column in the left filtering graph (AIRBNB)
	@app.callback(Output('air_filter_graph', 'figure'),
				  Input('air_filter_drop', 'value'))
	def change_filter_columns(new_column):
		return range_slider(Map_data.df_air, new_column)

	# Switch from column in the left filtering graph (RESTAURANTS)
	@app.callback(Output('res_filter_graph', 'figure'),
				  Input('res_filter_drop', 'value'),)
	def change_filter_columns(new_column):
		return range_slider(Map_data.df_res, new_column)

	# Switch the categorical variable wanted to be filtered (AIRBNB)
	@app.callback([Output('cat_air_drop','value'),
				   Output('cat_air_checklist', 'options'),
				   Output('cat_air_checklist', 'value')],
				  [Input('cat_air_drop', 'value'),
				   Input('air_reset_button', 'n_clicks')])
	def change_checkedlist(new_cat, reset):
		id_input = ctx.triggered_id
		if new_cat == None:
			return new_cat,[], []
		elif id_input == 'air_reset_button':
			return [], [], []
		else:
			return new_cat, Map_data.Filter_class.air_cat_options[new_cat], Map_data.Filter_class.air_limits[new_cat]

	@app.callback(Output('air_cat_on', 'children'),
				  [Input('cat_air_drop', 'value'),
				   Input('air_reset_button', 'n_clicks')])
	def cat_air_status(on, off):
		id_input = ctx.triggered_id
		if id_input == 'cat_air_drop':
			return 'CATEGORICAL FILTERING: ON'
		else:
			return 'CATEGORICAL FILTERING: OFF'

	# Switch the categorical variable wanted to be filtered (RESTAURANTS)
	@app.callback([Output('cat_res_drop', 'value'),
				   Output('cat_res_checklist', 'options'),
				   Output('cat_res_checklist', 'value')],
				  [Input('cat_res_drop', 'value'),
				   Input('res_reset_button', 'n_clicks')])
	def change_checkedlist(new_cat, reset):
		id_input = ctx.triggered_id
		if new_cat == None:
			return new_cat, [], []
		elif id_input == 'res_reset_button':
			return [], [], []
		else:
			return new_cat, Map_data.Filter_class.res_cat_options[new_cat], Map_data.Filter_class.res_limits[new_cat]

	@app.callback(Output('res_cat_on', 'children'),
				  [Input('cat_res_checklist', 'value'),
				   Input('res_reset_button', 'n_clicks')])
	def cat_air_status(on, off):
		id_input = ctx.triggered_id
		if id_input == 'cat_res_checklist':
			return 'CATEGORICAL FILTERING: ON'
		else:
			return 'CATEGORICAL FILTERING: OFF'

	app.run_server(debug=False)#Run the website