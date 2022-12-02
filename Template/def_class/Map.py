import pandas as pd

from dash import dcc
from dash import html
import dash_leaflet as dl
import dash_leaflet.express as dlx
import time


def N_airbnbs(Map_data, bounds):
	df = Map_data.df_air
	Count = df[(bounds[0][1]<df['long'])&(df['long']<bounds[1][1])
		&(bounds[0][0]<df['lat'])&(df['lat']<bounds[1][0])].shape[0]
	return Count

def import_restaurants():
	data = pd.read_csv('RestaurantsNew.csv')
	data = data[data['lon'].notna()]
	data = data[data['lat'].notna()]
	data = data.drop_duplicates(subset=['lon', 'lat'], keep='last')
	data = data.drop_duplicates(keep='last')
	return data

def import_airbnb():
	data = pd.read_csv('airbnb_open_data.csv')
	data = data[data['long'].notna()]
	data = data[data['lat'].notna()]
	data = data.drop_duplicates(subset=['long', 'lat'], keep='last')
	data = data.drop_duplicates(keep='last')
	return data

def df_to_geobuf(df, long):
	T_start = time.perf_counter()
	dicts = df.to_dict('rows')
	geojson = dlx.dicts_to_geojson(dicts, lon=long)  # convert to geojson
	geobuf = dlx.geojson_to_geobuf(geojson)  # convert to geobuf
	print("Time elapsed: {}".format(time.perf_counter()-T_start))
	return geobuf

class Map():
	"""docstring for Map"""
	def __init__(self):
		self.df_res = import_restaurants()
		self.df_air = import_airbnb()
		self.geobuf_res = df_to_geobuf(self.df_res, 'lon')
		self.geobuf_air = df_to_geobuf(self.df_air, 'long')

		self.url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
		self.attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '
		self.Data = self.geobuf_res
		self.Show = "Airbnbs"

		self.html_div =  html.Div(
			className="graph_card",
            children=[
                dl.Map(children=[
					dl.TileLayer(url=self.url, maxZoom=20, attribution=self.attribution),
					# dl.GestureHandling(),#Adds ctrl to zoom
					dl.GeoJSON(id="markers",data=self.Data, format="geobuf",cluster=True, zoomToBoundsOnClick=True,
			                   superClusterOptions={"radius": 400,"minPoints":20, "color": 'red'},),
				], center=(40.7, -74), zoom=11, style={'width': '100%', 'height': '100%', 'display': 'inline-block', 'position': 'absolute', 'z-index': '1'}, id='map'),
            	# html.H6('Switch', id='btn-switch'),
            	html.Button('Button 1', id='btn-switch', n_clicks=0),
            ],
		)

	def switch(self):
		if self.Show=="Restaurants":
			self.Data = self.geobuf_air
			self.Show = "Airbnbs"
			self.url='https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
			self.attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '
		else:
			self.Data = self.geobuf_res
			self.Show = "Restaurants"
			self.url=self.url='https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
			self.attribution=False
		return self.update()

	def update(self):
		return [
				dl.TileLayer(url=self.url, maxZoom=20, attribution=self.attribution),
				# dl.GestureHandling(),#Adds ctrl to zoom
				dl.GeoJSON(data=self.Data, format="geobuf",cluster=True, id="markers", zoomToBoundsOnClick=True,
		                   superClusterOptions={"radius": 400,"minPoints":20},),]
			
