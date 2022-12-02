import dash
from dash import dcc
from dash import html
from def_class.menu import make_menu_layout
import def_class.Map as Map
from def_class.Output import make_output_layout

from dash.dependencies import Input, Output
import json


if __name__ == '__main__':
	app = dash.Dash(__name__)
	app.title = "Group 44"
	Map_data = Map.Map()
	
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


#---Switch between restaurants and airbnbs---
	@app.callback([
		Output(component_id ='map', component_property='children'),
		Output('btn-switch', 'children'),
		Output('btn-switch', 'style'),
		Output('data_showing', 'children'),],
		Input('btn-switch', 'n_clicks'),
		)
	def update_map(N):
		Test = Map_data.switch()

		if Map_data.Show =='Restaurants':
			output_btn = "Show AirBnBs"
			style = {'border-color':'black',
				'color':'black'}
		else:
			output_btn = "Show Restaurants"
			style = {'border-color':'white',
				'color':'white'}
		return Test, output_btn, style,Map_data.Show

#---Get amount of Airbnbs in region---
	@app.callback(
		Output('Nairbnb', 'children'),
		Input('map', 'bounds'),
		)
	def update_bounds(bounds):
		Count = Map.N_airbnbs(Map_data,bounds)
		return "Airbnbs in visible region: {}".format(Count)


#---Data overing over marker---
	@app.callback(Output("bounds", "children"), [Input("markers", "hover_feature")])
	def update_tooltip(feature):
		if Map_data.Show=='Restaurants':
			if feature is None:
				pass
			elif feature['properties']['cluster']==True:
				pass
			else:
				return str(feature['properties']['DBA'])


	app.run_server(debug=False, dev_tools_ui=False)