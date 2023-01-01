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


def N_airbnbs(Map_data, bounds):#Calculate amount of airbnbs in region
	df = Map_data.df_air
	Count = df[(bounds[0][1]<df['long'])&(df['long']<bounds[1][1])
		&(bounds[0][0]<df['lat'])&(df['lat']<bounds[1][0])].shape[0]
	return Count

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
	T_start = time.perf_counter()#start timer
	dicts = df.to_dict('rows')
	geojson = dlx.dicts_to_geojson(dicts, lon=long)  # convert to geojson
	print("Time elapsed: {}".format(time.perf_counter()-T_start))
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
		self.Bins_price = 50
		self.Bins_fee = 40
		self.Bins_score = 25

		self.url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png' #The style of the map
		self.attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '#Add reference to the styling of the map 
		self.Data = copy.deepcopy(self.geojson_res)
		self.Show = "Restaurants"
		self.filter = assign("function(feature, context){{return true;}}")
		map_data = self.update()
		self.int_col = ['price', 'service_fee']

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

			#AirBnB Controls Objects
			html.Div(id='ctrl_div_air', style={'display': 'none'}, children=[
							html.Div(id='legality', style={'display': 'block'}, children=[
							html.Center(children=[
							html.H4("Advanced controls", style={'margin-left': '1.5rem'}),
							html.Hr(),
							html.P("Legality Warning:"),
							dcc.RadioItems(['Warning On', 'Warning Off'],
								   'Warning Off',
								   inline=True,
								   id='legality_radio')
							])
							]),
						 	 html.Div(id='ctrl_adv', children=[
							 # html.H4("Advanced controls", style={'margin-left': '1.5rem'}),
							 # html.Hr(),
							 dcc.Dropdown(self.int_col,
                						  'price',
               							id='dropdown',
            							 ),
							 dcc.Graph(id='graph'),
							 ]),
							 html.Div(id='ctrl_price', style={'display': 'block'},  children=[
							 html.P("Price Slider:"),
							 dcc.RangeSlider(min = min(self.df_air['price']),
											 max = max(self.df_air['price']),
											 step = self.Bins_price,
											 value=[min(self.df_air['price']), max(self.df_air['price'])],
											 tooltip={"placement": "top", "always_visible": True},
											 allowCross=False,
											 id='slider_price'
											 )]),
				            html.Div(id='ctrl_fee', style={'display': 'block'}, children=[
							html.P("Service Fee Slider:"),
							dcc.RangeSlider(min = min(self.df_air['service_fee']),
											max = max(self.df_air['service_fee']),
											step = self.Bins_fee,
											value=[min(self.df_air['service_fee']), max(self.df_air['service_fee'])],
											tooltip={"placement": "top", "always_visible": True},
											allowCross=False,
											id='slider_fee'
											)]),

							]),

			# Restaurants Control Objects
			html.Div(id='ctrl_div_res', style={'display': 'none'}, children=[
				html.P("Grade Control:"),
				dcc.Graph(id='bar_grade'),
				dcc.Checklist(
					id="checklist",
					options=[
						{'label': 'A', 'value': 'A'},
						{'label': 'B', 'value': 'B'},
						{'label': 'C', 'value': 'C'},
						{'label': 'U', 'value': 'U'},
					],
					value=['A', 'B', 'C', 'U'],
					labelStyle={"display": "inline-block"},
				),
				html.P("Score Control:"),
				dcc.Graph(id='score_graph', figure = px.histogram(self.df_res, x="SCORE", nbins=self.Bins_score)),
				dcc.RangeSlider(min=min(self.df_res['SCORE']),
								max=max(self.df_res['SCORE']),
								step = 9,
								value=[min(self.df_res['SCORE']), max(self.df_res['SCORE'])],
								tooltip={"placement": "top", "always_visible": True},
								allowCross=False,
								id='slider_score'
								),
			])


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
		return [
				dl.TileLayer(url=self.url, maxZoom=20,minZoom=10, attribution=self.attribution),
				# dl.GestureHandling(),#Adds ctrl to zoom
				dl.GeoJSON(data=self.Data,cluster=True, id="markers", zoomToBoundsOnClick=True,
							superClusterOptions={"radius": 400,"minPoints":20},
							children=[html.Div(id='hide_tooltip',children=[dl.Tooltip(id="tooltip")])]),]

	def update_filter(self,price_range): #Price filter for AirBnBs
		if self.Show =="Airbnbs":
			self.Data['features'] = copy.deepcopy([data for data in self.geojson_air['features'] if (data['properties']['price'] >= price_range[0] and data['properties']['price'] <= price_range[1])])
			#print("Time to filter: {}".format(time.perf_counter() - T_start))
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

