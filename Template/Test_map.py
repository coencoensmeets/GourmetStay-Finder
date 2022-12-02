import dash
from dash import dcc
from dash import html
from jbi100_app.views.menu import make_menu_layout
import plotly.express as px
import pandas as pd

import dash_leaflet as dl
import dash_leaflet.express as dlx

if __name__ == '__main__':
	data = pd.read_csv('RestaurantsNew.csv')
	data = data[data['lon'].notna()]
	data = data[data['lat'].notna()]
	data = data.drop_duplicates(subset=['lon', 'lat'], keep='last')
	data = data.drop_duplicates(keep='last')

	dicts = data.to_dict('rows')
	geojson = dlx.dicts_to_geojson(dicts, lon="lon")  # convert to geojson
	geobuf = dlx.geojson_to_geobuf(geojson)  # convert to geobuf

	url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
	attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '


	app = dash.Dash(__name__)
	app.layout = html.Div([
	dl.Map([
		dl.TileLayer(url=url, maxZoom=20, attribution=attribution),
		# dl.GestureHandling(),#Adds ctrl to zoom
		dl.GeoJSON(data=geobuf, format="geobuf",cluster=True, id="sc", zoomToBoundsOnClick=True,
                   superClusterOptions={"radius": 400,"minPoints":20}),
	], center=(40.7, -74), zoom=11, style={'width': '900px', 'height': '800px'}),
	])

	# app.layout = html.Div([
	# 	dcc.Graph(figure=fig, className="full")
	# ])
	app.run_server(debug=False)