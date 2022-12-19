import dash
from dash import dcc, html, ctx
from def_class.menu import make_menu_layout
import def_class.Middle as Map
from def_class.Output import make_output_layout

from dash.dependencies import Input, Output, State
import numpy as np
import plotly.express as px
import json



#Saving data throughout the main interactions of the program. 
class Save_data():
	def __init__(self):
		self.Data = [] #Hover data (mouse of item)
		self.n_clicked = 0 #The amount of times the switch button has been clicked
		self.n_clicked_ctrl = 0 #The amount of times the advanced control button has been clicked
		self.feature = {} #Last feature that was hovered over

	def update_hover(self, data): #Updates the hover data
		self.Data = data

	def update_click(self,data): #Updates Clicked data
		self.Data = data

	def update_clicked(self, n=1): #Updates the click counter for switching maps
		self.n_clicked +=n

	def update_clicked_ctrl(self, n=1): #Updates the click counter for switching advanced controls
		self.n_clicked_ctrl +=n

	def update_click_feature(self, feature):#Updates the last feature that was hovered over
		print("Updated: {}".format(feature))
		self.feature = feature

if __name__ == '__main__':
	#---Main Setup---
	app = dash.Dash(__name__)
	app.title = "Group 44"
	Map_data = Map.Map()

	Data_saved = Save_data() #Setup for the storing of data class 
	
	#Layout creation
	app.layout = html.Div(
		id="app-container",  
		children=[
		#Hidden DIV for OUTPUT Callback
			html.Div(id='hidden-div', style={'display':'none'}),
			# Left column
			html.Div(

				id="left-column",
				className="two columns",
				children=make_menu_layout()
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
	)

#------INTERACTIONS-------
	#-Switch between restaurants and airbnbs & Number of airbnbs+minimap---
	@app.callback([
		Output(component_id ='map', component_property='children'),#Main map component
		Output('btn-switch', 'children'),#Text of the button (Restaurant/airbnb)
		Output('btn-switch', 'style'),#Style of the button (White/dark)
		Output('data_showing', 'children'),#"Currently showing ... map" text
		Output('mini-map', 'children'),#Minimap component
		Output('Nairbnb', 'children'), #Amount of airbnbs text
		],[
		Input('btn-switch', 'n_clicks'),#The switch from map button input (amount of clicks)
		Input('map', 'bounds'),],#The bounds of the map input (Bounds)
		[State(component_id ='map', component_property='children'),
		State('btn-switch', 'children'),
		State('btn-switch', 'style'),
		State('mini-map', 'children'),
		State('Nairbnb', 'children')]
		)
	def update_map(N, bounds, Map_data_list, output_btn, style, Mini, N_airbnb):
		id_input = ctx.triggered_id

		if (id_input=='btn-switch'):
			if N!= Data_saved.n_clicked and N!=0:#Checks whether the button has been clicked and not the loading of the page
				print("Switch")
				Map_data_list = Map_data.switch()#Get the new html data for the new map
				Data_saved.update_clicked()#Update the saved click counter

				if Map_data.Show =='Restaurants':#If the restaurants are shown
					output_btn = "Show AirBnBs"
					style = {'border-color':'black',
						'color':'black'} #Change the colour of the button to be visible on the background
					feature = Data_saved.feature#Get last feature that is clicked upon over (only airbnb)
					if bool(feature):#Check whether a feature has been clicked upon
						if not feature['properties']['cluster']:#Check whether it is not a cluster
							geojsonlast = Map.get_house_data(feature)#Get the html data for the house icon marker
							Map_data_list.append(geojsonlast)

				else:#Checks whether Airbnbs are shown
					output_btn = "Show Restaurants"
					style = {'border-color':'white',
						'color':'white'}#change colour of button to be visible on background
		if (id_input=='map'):
			Mini = Map_data.update_bounds_mini(bounds) #With the bounds update the minimap (Output is html data for the minimap)
			Count = Map.N_airbnbs(Map_data,bounds) #Calculates amount of airbnbs in shown region
			N_airbnb = "Airbnbs in visible region: {}".format(Count)

		return Map_data_list, output_btn, style,Map_data.Show, Mini, N_airbnb

	#Switch advanced<->map
	@app.callback(
		[Output('map_div', 'style'),#Style of the map div
		Output('ctrl_div', 'style')],#Style of the ctrl div
		[Input('btn-controls', 'n_clicks')])#Input click on button of advanced controls
	def switch_map_advanced(N):
		if N!= Data_saved.n_clicked_ctrl and N!=0:#Checks whether the button has been clicked and not the loading of the page
			print("Clicked")
			Data_saved.update_clicked_ctrl()#Update the click counter
		else:
			print("Not clicked")

		if Data_saved.n_clicked_ctrl%2 ==0:#Map is shown
			Output = [{'display': 'block'}, {'display': 'none'}]#Make map visible and hide the control dib
		else:#Control is shown
			Output = {'display': 'none'}, {'display': 'block'}#Hide map and make control div visible
		return (*Output,)		

	@app.callback([Output("Information", "children"), #Information div
		Output('tooltip', 'children')], #Tooltop (hovering extension)
		[Input("markers", "hover_feature"), #Input when a feature is hovered over
		 Input("markers", "click_feature")]) #Input when a feature is clicked on
	def update_tooltip(hover_feature,click_feature):
		if hover_feature is None and click_feature is None:
			return Data_saved.Data, None  # return last information and no tooltip
		if click_feature is None or (click_feature != hover_feature and hover_feature is not None):
			if hover_feature['properties']['cluster'] == True:  # Check whether the feature is a cluster
				return Data_saved.Data, [
					html.P('#N={}'.format(hover_feature['properties']['point_count']))]  # Returns cluster information
			elif Map_data.Show == 'Restaurants':  # Restaurant map is shown
				# Creates the html for the information
				Output = [
					html.B("NOT SELECTED"),
					html.P("Name: {}".format(str(hover_feature['properties']['DBA']).lower())),
					html.P("Score: {}".format(hover_feature['properties']['SCORE'])),
					html.P("Cuisine: {}".format(hover_feature['properties']['CUISINE_DESCRIPTION'])),
					html.A(href="https://www.google.com/search?q={} {} {} NYC".format(
						hover_feature['properties']['DBA'],
						hover_feature['properties']['BUILDING'],
						hover_feature['properties']['STREET']).lower()
						   , children=[
							html.Button("Google")
						])]
				# print(feature)
				Data_saved.update_hover(Output)  # update last hover feature
				return Data_saved.Data, Data_saved.Data[0:4]
			else:  # Airbnb map is shown
				# Creates the html for the information
				Output = [
					html.B("NOT SELECTED"),
					html.P("Name: {}".format(str(hover_feature['properties']['NAME']).lower())),
					html.P("Price: {}".format(hover_feature['properties']['price'])),
					html.P("Rating: {}".format(hover_feature['properties']['review_rate_number']))
				]
				Data_saved.update_hover(Output)  # Updates last hover feature
				return Data_saved.Data, Data_saved.Data[0:4]
		else:
			if click_feature['properties']['cluster'] == True:  # Check whether the feature is a cluster
				return Data_saved.Data, [
					html.P('#N={}'.format(click_feature['properties']['point_count']))]  # Returns cluster information
			elif Map_data.Show == 'Restaurants':  # Restaurant map is shown
				# Creates the html for the information
				Output = [
					html.B("SELECTED"),
					html.P("Name: {}".format(str(click_feature['properties']['DBA']).lower())),
					html.P("Score: {}".format(click_feature['properties']['SCORE'])),
					html.P("Cuisine: {}".format(click_feature['properties']['CUISINE_DESCRIPTION'])),
					html.A(href="https://www.google.com/search?q={} {} {} NYC".format(
						click_feature['properties']['DBA'],
						click_feature['properties']['BUILDING'],
						click_feature['properties']['STREET']).lower()
						   , children=[
							html.Button("Google")
						])]
				# print(feature)
				Data_saved.update_click(Output)  # update last hover feature
				return Data_saved.Data, Data_saved.Data[0:4]
			else:  # Airbnb map is shown
				# Creates the html for the information
				Output = [
					html.B("SELECTED"),
					html.P("Name: {}".format(str(click_feature['properties']['NAME']).lower())),
					html.P("Price: {}".format(click_feature['properties']['price'])),
					html.P("Rating: {}".format(click_feature['properties']['review_rate_number']))
				]
				Data_saved.update_click(Output)  # Updates last hover feature
				return Data_saved.Data, Data_saved.Data[0:4]

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


	@app.callback(
	Output('graph', 'figure'),
	Input('slider_price', 'value'))
	def display_color(slider_price):
		data_air = Map_data.df_air
		fig = px.histogram(data_air,
						   x='price',
						   range_x=[slider_price[0], slider_price[1]],
						   nbins = 50,
						   labels={'x':'Price', 'y':'Count of Listings'},
						   title = 'Interactive Price Distribution')
		return fig

	app.run_server(debug=False, dev_tools_ui=False)#Run the website