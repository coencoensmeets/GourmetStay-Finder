import pandas as pd

from dash import dcc
from dash import html
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign
import time
import numpy as np


def N_airbnbs(Map_data, bounds):#Calculate amount of airbnbs in region
	df = Map_data.df_air
	Count = df[(bounds[0][1]<df['long'])&(df['long']<bounds[1][1])
		&(bounds[0][0]<df['lat'])&(df['lat']<bounds[1][0])].shape[0]
	return Count

def import_restaurants():#importing the restaurant data
	data = pd.read_csv('RestaurantsNew.csv')
	data = data[data['lon'].notna()]
	data = data[data['lat'].notna()]
	data = data.drop_duplicates(subset=['lon', 'lat'], keep='last')
	data = data.drop_duplicates(keep='last')

	return data

def import_airbnb():
	data = pd.read_csv('airbnb_open_data.csv') #importing the airbnb Data
	data = data[1:5000] #Line only for testing to save time
	data = data[data['long'].notna()]
	data = data[data['lat'].notna()]

	# Removing true duplicated for geographical position lat & long:
	columns = ['lat', 'long', 'service fee', 'NAME', 'host name']
	data = data.drop_duplicates(subset=columns)
	data = data.replace(np.nan, 30)

	#Replacing the dolar sign. Changing fee to float and removing dollar sign price
	data['service fee'][data['service fee'].notnull()] = data['service fee'][data['service fee'].notnull()]\
		.replace("[$,]", "", regex=True).astype(float)

	data['price'][data['price'].notnull()] = data['price'][data['price'].notnull()] \
		.replace("[$,]", "", regex=True).astype(float)

	# Removing duplicated for the ID column:
	data = data.drop_duplicates(subset='id')

	# Adding a column for legality warning
	query = (data['minimum nights'] <= 30.0) & (data['room type'] == 'Entire home/apt')
	data['legality'] = query
	print(data['service fee'])

	return data

def df_to_geobuf(df, long):#convert pandas dataframe to geobuf
	T_start = time.perf_counter()#start timer
	dicts = df.to_dict('rows')
	geojson = dlx.dicts_to_geojson(dicts, lon=long)  # convert to geojson
	geobuf = dlx.geojson_to_geobuf(geojson)  # convert to geobuf
	print("Time elapsed: {}".format(time.perf_counter()-T_start))
	return geobuf


def get_house_data(feature):#Create the html data for house icon on restaurant map
	features = [dict(name=feature['properties']['NAME'], lat=feature['geometry']['coordinates'][1], lon=feature['geometry']['coordinates'][0])]
	# Generate geojson with a marker for each country and name as tooltip.
	print(features)
	geojsonhouse = dlx.dicts_to_geojson([{**feat, **dict(tooltip=feat['name'])} for feat in features])
	draw_flag = assign("""function(feature, latlng){
	const flag = L.icon({iconUrl: `https://i.pinimg.com/originals/b3/cc/d5/b3ccd57b054a73af1a0d281265b54ec8.jpg`, iconSize: [64, 48]});
	return L.marker(latlng, {icon: flag});
	}""")
	geojson_data = dl.GeoJSON(data=geojsonhouse, options=dict(pointToLayer=draw_flag),zoomToBounds=False)
	return geojson_data

class Map():
	"""docstring for Map"""
	def __init__(self):
		self.df_res = import_restaurants()
		self.df_air = import_airbnb()
		self.geobuf_res = df_to_geobuf(self.df_res, 'lon')
		self.geobuf_air = df_to_geobuf(self.df_air, 'long')

		self.url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png' #The style of the map
		self.attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '#Add reference to the styling of the map 
		self.Data = self.geobuf_res
		self.Show = "Restaurants"

		map_data = self.update()

		# Initial polygon creation for the minimap
		polygon = dl.Polygon(color="#ff7800", weight=1, positions=[[40.43963107298772,-74.21127319335939], [40.43963107298772,-73.7889862060547], [40.95967830900992,-73.7889862060547], 
											[40.95967830900992,-74.21127319335939], [40.43963107298772,-74.21127319335939]])
		patterns = [dict(offset='0', repeat='10', dash=dict(pixelSize=0))]
		self.inner_ring = dl.PolylineDecorator(children=polygon, patterns=patterns)

		#Creation of the html div for the entire middle part.
		self.html_div =  [
			html.Div(
				id='map_div',
				style={'display': 'block'},
				className="graph_card",
				children=[
					dl.Map(children=[
						dl.TileLayer(url=self.url, maxZoom=20, attribution=self.attribution),
						self.inner_ring
						# dl.GestureHandling(),#Adds ctrl to zoom,
					], center=(40.7, -74), zoom=8, style={'border-width': '5px','border-style':'solid','border-color':'#f9f9f9','top':"80%",'width': '20%', 'height': '20%', 'display': 'inline-block', 'position': 'absolute', 'z-index': '1000'}, id='mini-map'),

					dl.Map(children=[
						dl.TileLayer(url=self.url, maxZoom=20, minZoom=10,attribution=self.attribution),
						# dl.GestureHandling(),#Adds ctrl to zoom
						dl.GeoJSON(data=self.Data, format="geobuf",cluster=True, id="markers", zoomToBoundsOnClick=True,
									superClusterOptions={"radius": 400,"minPoints":20},
							children=[html.Div(id='hide_tooltip',children=[dl.Tooltip(id="tooltip")])]),
					], center=(40.7, -74), zoom=11, style={'width': '100%', 'height': '100%', 'display': 'inline-block', 'position': 'absolute', 'z-index': '1'}, id='map'),
					# html.H6('Switch', id='btn-switch'),
					html.Div(className='btn-wrapper',children=[
						html.Button('Button 1', id='btn-switch', n_clicks=0),
					])
				],
			),
			#Create div for the control
			html.Div(id='ctrl_div',
				style={'display': 'none'},
				children=[
				html.Div(id='ctrl_adv',children=[
					html.H4("Advanced controls", style={'margin-left': '1.5rem'}),
					html.Hr(),
				])])
		]

	#Switch from restaurant to airbnb map
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

	#Get the html of the map
	def update(self):
		return [
				dl.TileLayer(url=self.url, maxZoom=20,minZoom=10, attribution=self.attribution),
				# dl.GestureHandling(),#Adds ctrl to zoom
				dl.GeoJSON(data=self.Data, format="geobuf",cluster=True, id="markers", zoomToBoundsOnClick=True,
							superClusterOptions={"radius": 400,"minPoints":20},
							children=[html.Div(id='hide_tooltip',children=[dl.Tooltip(id="tooltip")])]),]
		
	#Update the minimap polygon returns html for the entire minimap
	def update_bounds_mini(self,bounds):
		polygon = dl.Polygon(color="#ff7800", weight=1, positions=[[bounds[0][0],bounds[0][1]], [bounds[0][0],bounds[1][1]], [bounds[1][0],bounds[1][1]], 
											[bounds[1][0],bounds[0][1]], [bounds[0][0],bounds[0][1]]])
		patterns = [dict(offset='0', repeat='10', dash=dict(pixelSize=0))]
		self.inner_ring = dl.PolylineDecorator(children=polygon, patterns=patterns)
		return [dl.TileLayer(url=self.url, maxZoom=20, attribution=self.attribution),
						self.inner_ring]

