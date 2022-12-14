import dash
from dash import dcc
from dash import html
from def_class.menu import make_menu_layout
import def_class.Middle as Map
from def_class.Output import make_output_layout

from dash.dependencies import Input, Output
import numpy as np
import json

class Save_data():
	def __init__(self):
		self.Data = []
		self.n_clicked = 0
		self.n_clicked_ctrl = 0
		self.feature = {}

	def update_hover(self, data):
		self.Data = data

	def update_clicked(self, n=1):
		self.n_clicked +=n

	def update_clicked_ctrl(self, n=1):
		self.n_clicked_ctrl +=n

	def update_hover_feature(self, feature):
		self.feature = feature

if __name__ == '__main__':
	app = dash.Dash(__name__)
	app.title = "Group 44"
	Map_data = Map.Map()

	Data_saved = Save_data()
	
	app.layout = html.Div(
		id="app-container",
		children=[
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
		Output(component_id ='map', component_property='children'),
		Output('btn-switch', 'children'),
		Output('btn-switch', 'style'),
		Output('data_showing', 'children'),
		Output('mini-map', 'children'),
		Output('Nairbnb', 'children'),
		],[
		Input('btn-switch', 'n_clicks'),
		Input('map', 'bounds'),]
		)
	def update_map(N, bounds):
		print(N)
		print(bounds)

		if N!= Data_saved.n_clicked and N!=0:
			Map_data_list = Map_data.switch()
			Data_saved.update_clicked()
		else:
			Map_data_list = Map_data.update()

		Mini = Map_data.update_bounds_mini(bounds)
		Count = Map.N_airbnbs(Map_data,bounds)
		N_airbnb = "Airbnbs in visible region: {}".format(Count)

		if Map_data.Show =='Restaurants':
			output_btn = "Show AirBnBs"
			style = {'border-color':'black',
				'color':'black'}
		else:
			output_btn = "Show Restaurants"
			style = {'border-color':'white',
				'color':'white'}

		# feature = Data_saved.feature
		# geojson = Map.get_house_dat(feature)

		# geojson_data = dl.GeoJSON(data=geojson, options=dict(pointToLayer=draw_flag), zoomToBounds=True)
		# Map_data_list.append(geojson_data)
		return Map_data_list, output_btn, style,Map_data.Show, Mini, N_airbnb

	#Switch advanced<->map
	@app.callback(
		[Output('map_div', 'style'),
		Output('ctrl_div', 'style')],
		[Input('btn-controls', 'n_clicks')])
	def switch_map_advanced(N):
		if N!= Data_saved.n_clicked_ctrl and N!=0:
			print("Clicked")
			Data_saved.update_clicked_ctrl()
		else:
			print("Not clicked")

		if Data_saved.n_clicked_ctrl%2 ==0:
			Output = [{'display': 'block'}, {'display': 'none'}]
		else:
			Output = {'display': 'none'}, {'display': 'block'}
		return (*Output,)		

	#---Data overing over marker---
	@app.callback([Output("bounds", "children"), Output('tooltip', 'children')], [Input("markers", "hover_feature")])
	def update_tooltip(feature):
		# print(feature)
		if feature is None:
			return Data_saved.Data,None
		elif feature['properties']['cluster']==True:
			return Data_saved.Data, [html.P('#N={}'.format(feature['properties']['point_count']))]
		elif Map_data.Show=='Restaurants':
			Output = [
			html.P("Name: {}".format(str(feature['properties']['DBA']).lower())),
			html.P("Score: {}".format(feature['properties']['SCORE'])),
			html.P("Cuisine: {}".format(feature['properties']['CUISINE DESCRIPTION'])),
			html.A(href = "https://www.google.com/search?q={} {} {} NYC".format(
					feature['properties']['DBA'],
					feature['properties']['BUILDING'],
					feature['properties']['STREET']).lower()
				,children=[
			html.Button("Google")
			])]
			# print(feature)
			Data_saved.update_hover(Output)
			return Data_saved.Data, Data_saved.Data[0:3]
		else:
			Data_saved.update_hover_feature(feature)
			Output = [
			html.P("Name: {}".format(str(feature['properties']['NAME']).lower())),
			html.P("Price: {}".format(feature['properties']['price'])),
			html.P("Rating: {}".format(feature['properties']['review rate number']))
			]
			Data_saved.update_hover(Output)
			return Data_saved.Data, Data_saved.Data[0:3]

	app.run_server(debug=False, dev_tools_ui=False)