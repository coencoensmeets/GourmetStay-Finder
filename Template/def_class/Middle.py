import pandas as pd

from dash import dcc, html, ctx
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign
import time
import numpy as np
import dash_daq as daq
import plotly.express as px

import copy

class filtering_limits():
	def __init__(self, df_air, df_res):
		self.air_columns = ['price', 'service_fee', 'minimum_nights','Construction_year', 'number_of_reviews', 'calculated_host_listings_count']
		self.res_columns = ['SCORE']

		self.air_limits = {k: [df_air[k].min(), df_air[k].max()] for k in self.air_columns}
		self.res_limits = {k: [df_res[k].min(), df_res[k].max()] for k in self.res_columns}

	def update_air(self, column, range):
		self.air_limits[column] = range
	
	def update_res (self, column, range):
		self.res_limits[column] = range

def filter_data(geojson_feat, filter, bounds=[[-100,-100],[100,100]]): #-73.9778886, 40.7635365
	T_start = time.perf_counter()
	List = []
	for data in geojson_feat:
		conditions = [
			data['geometry']['coordinates'][0]>=bounds[0][1],
			data['geometry']['coordinates'][1]>=bounds[0][0],
			data['geometry']['coordinates'][0]<=bounds[1][1],
			data['geometry']['coordinates'][1]<=bounds[1][0]
		]
		for k, v in filter:
			conditions.extend([data['properties'][k] >= v[0], data['properties'][k]<= v[1]])

		if all(conditions):
			List.append(data)
	print("Time it took to filter: {}".format(time.perf_counter()-T_start))
	return List


def N_airbnbs(Map_data, bounds):#Calculate amount of airbnbs in region
	N_air = len(filter_data(Map_data.geojson_air['features'], Map_data.Filter_class.air_limits.items(), bounds))
	return N_air

def import_restaurants():#importing the restaurant data
	data = pd.read_csv('RestaurantsNew.csv')
	data = data[data['lon'].notna()]
	data = data[data['lat'].notna()]
	data.dropna()
	data = data.drop_duplicates(subset=['lon', 'lat'], keep='last')
	data = data.drop_duplicates(keep='last')
	data.columns = data.columns.str.replace(' ', '_')
	data['SCORE'] = data['SCORE'].fillna(0)
	data['SCORE'].astype(int)
	#Restaurants with pending grades are all put under the U for unknown
	data['GRADE'] = data['GRADE'].fillna('U')
	data['GRADE'] = data['GRADE'].replace({'Not Yet Graded': 'U'})
	data['GRADE'] = data['GRADE'].replace({'P': 'U'})
	data['GRADE'] = data['GRADE'].replace({'Z': 'U'})
	data['SCORE'] = data['SCORE'].replace({-1: 0})

	# Index(['CAMIS', 'DBA', 'BORO', 'BUILDING', 'STREET', 'ZIPCODE', 'PHONE',
	#        'CUISINE_DESCRIPTION', 'INSPECTION_DATE', 'ACTION', 'VIOLATION_CODE',
	#        'VIOLATION_DESCRIPTION', 'CRITICAL_FLAG', 'SCORE', 'GRADE',
	#        'GRADE_DATE', 'RECORD_DATE', 'INSPECTION_TYPE', 'lat', 'lon']

	# print('letter are: ', data['GRADE'].unique()) #, data['SCORE'].head())
	# print('The minimum is: ', min(data['SCORE']), 'the maximum is: ', max(data['SCORE']))
	# print(min(data['GRADE']), max(data['GRADE']), min(data['SCORE']), max(data['SCORE']))
	return data

def import_airbnb():
	data = pd.read_csv('airbnb_open_data.csv') #importing the airbnb Data
	# data = data[1:5000] #Line only for testing to save time
	data = data[data['long'].notna()]
	data = data[data['lat'].notna()]

	# Removing true duplicated for geographical position lat & long:
	columns = ['lat', 'long', 'service fee', 'NAME', 'host name']
	data = data.drop_duplicates(subset=columns)
	data = data.replace(np.nan, 30)
	data.dropna()

	#Replacing the dollar sign. Changing fee to float and removing dollar sign price
	data['service fee'][data['service fee'].notnull()] = data['service fee'][data['service fee'].notnull()]\
		.replace("[$,]", "", regex=True).astype(float)

	data['price'][data['price'].notnull()] = data['price'][data['price'].notnull()]\
		.replace("[$,]", "", regex=True).astype(float)

	# Removing duplicated for the ID column:
	data = data.drop_duplicates(subset='id')

	# Adding a column for legality warning
	query = (data['minimum nights'] <= 30.0) & (data['room type'] == 'Entire home/apt')
	data['legality'] = query
	data['trustworthiness'] = query

	data.columns = data.columns.str.replace(' ', '_')
	return data

def df_to_geojson(df, long):#convert pandas dataframe to geojson
	print("Start Converting to geojson", end="\r\r")
	T_start = time.perf_counter()#start timer
	dicts = df.to_dict('rows')
	geojson = dlx.dicts_to_geojson(dicts, lon=long)  # convert to geojson
	print("Time elapsed to convert to geojson: {}s".format(time.perf_counter()-T_start))
	return geojson


def get_house_data(feature):#Create the html data for house icon on restaurant map
	features = [dict(name=feature['properties']['NAME'], lat=feature['geometry']['coordinates'][1], lon=feature['geometry']['coordinates'][0])]
	# Generate geojson with a marker for each country and name as tooltip.
	print(features)
	geojsonhouse = dlx.dicts_to_geojson([{**feat, **dict(tooltip=feat['name'])} for feat in features])
	draw_flag = assign("""function(feature, latlng){
	const flag = L.icon({iconUrl: `https://www.shareicon.net/download/2015/12/20/690629_home_512x512.png`, iconSize: [70, 60]});
	return L.marker(latlng, {icon: flag});
	}""")
	#https://i.pinimg.com/originals/b3/cc/d5/b3ccd57b054a73af1a0d281265b54ec8.jpg
	geojson_data = dl.GeoJSON(data=geojsonhouse, options=dict(pointToLayer=draw_flag),zoomToBounds=False)
	return geojson_data

class Map():
	"""docstring for Map"""
	def __init__(self):
		self.df_res = import_restaurants()
		self.df_air = import_airbnb()
		self.res_col = self.df_res['GRADE'].value_counts().rename_axis('Grade').to_frame('counts') #Creating extra dataframe for grades frequencies.
		self.res_col['GRADE'] = ['A', 'B', 'C', 'U']
		self.geojson_res = df_to_geojson(self.df_res, 'lon')
		self.geojson_air = df_to_geojson(self.df_air, 'long')

		self.Filter_class = filtering_limits(self.df_air, self.df_res)

		self.Bins_price = 50
		self.Bins_fee = 40
		self.Bins_score = 25

		self.url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png' #The style of the map
		self.attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '#Add reference to the styling of the map 
		self.Data = copy.deepcopy(self.geojson_res)
		self.Show = "Restaurants"
		self.filter = assign("function(feature, context){{return true;}}")
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
						dl.GeoJSON(data=self.Data,cluster=True, id="markers", zoomToBoundsOnClick=True,
									superClusterOptions={"radius": 400,"minPoints":20},
							children=[html.Div(id='hide_tooltip',children=[dl.Tooltip(id="tooltip")])]),
					], center=(40.7, -74), zoom=11, style={'width': '100%', 'height': '100%', 'display': 'inline-block', 'position': 'absolute', 'z-index': '1'}, id='map'),
					# html.H6('Switch', id='btn-switch'),
					html.Div(className='btn-wrapper',children=[
						html.Button('Show Airbnbs', id='btn-switch', n_clicks=0),
					])
				],
			),
		]

	#Switch from restaurant to airbnb map
	def switch(self):
		if self.Show=="Restaurants":
			T_start = time.perf_counter()
			# print(self.geojson_air['features'])
			#self.Data['features'] = copy.deepcopy([data for data in self.geojson_air['features'] if data['properties']['price']>1000])
			self.Data = copy.copy(self.geojson_air)
			#self.Data = self.geojson_air
			print("Time to filter: {}".format(time.perf_counter()-T_start))
			self.Show = "Airbnbs"
			self.url='https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
			self.attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '
		else:
			#self.Data = copy.copy(self.geojson_res)
			self.data = self.geojson_res
			self.Show = "Restaurants"
			self.url='https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
			self.attribution=False
		return self.update()

	#Get the html of the map
	def update(self):
		if self.Show=='Restaurants':
			self.Data['features'] = filter_data(self.geojson_res['features'], self.Filter_class.res_limits.items())

		else:
			self.Data['features'] = filter_data(self.geojson_air['features'], self.Filter_class.air_limits.items())

		return [
				dl.TileLayer(url=self.url, maxZoom=20,minZoom=10, attribution=self.attribution),
				# dl.GestureHandling(),#Adds ctrl to zoom
				dl.GeoJSON(data=self.Data,cluster=True, id="markers", zoomToBoundsOnClick=True,
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

