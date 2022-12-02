import pandas as pd

from dash import dcc
from dash import html
import dash_leaflet as dl
import dash_leaflet.express as dlx

class Map(object):
	"""docstring for Map"""
	def __init__(self):
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

		self.html_div = html.Div([
			dl.Map([
				dl.TileLayer(url=url, maxZoom=20, attribution=attribution),
				# dl.GestureHandling(),#Adds ctrl to zoom
				dl.GeoJSON(data=geobuf, format="geobuf",cluster=True, id="sc", zoomToBoundsOnClick=True,
		                   superClusterOptions={"radius": 400,"minPoints":20}),
			], center=(40.7, -74), zoom=11, style={'width': '100%', 'height': '100%', 'display': 'inline-block', 'position': 'absolute'}),
		])
