import pandas as pd

from dash import dcc, html, ctx
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign
import time
import numpy as np
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
from def_class.menu import create_popover

import copy


class filtering_limits():
    def __init__(self, df_air, df_res):
        self.air_columns = ['price', 'service_fee', 'minimum_nights', 'Construction_year', 'number_of_reviews',
                            'calculated_host_listings_count']
        self.res_columns = ['SCORE']

        self.air_cat_columns = ['host_identity_verified', 'neighbourhood_group', 'cancellation_policy',
                                'instant_bookable', 'room_type']
        self.res_cat_columns = ['BORO', 'CUISINE_DESCRIPTION', 'ACTION', 'CRITICAL_FLAG', 'GRADE']

        self.air_limits = {k: [df_air[k].min(), df_air[k].max()] for k in self.air_columns}
        self.res_limits = {k: [df_res[k].min(), df_res[k].max()] for k in self.res_columns}

        self.air_cat_options = {k: df_air[k].unique().tolist() for k in self.air_cat_columns}
        self.res_cat_options = {k: df_res[k].unique().tolist() for k in self.res_cat_columns}

        self.air_limits = dict(self.air_limits, **self.air_cat_options)
        self.res_limits = dict(self.res_limits, **self.res_cat_options)

    def update_cat_air(self, column, chosen):
        if column == None and chosen == None:
            self.air_limits = dict(self.air_limits, **self.air_cat_options)
        else:
            self.air_limits[column] = chosen

    def update_cat_res(self, column, chosen):
        if column == None and chosen == None:
            self.res_limits = dict(self.res_limits, **self.res_cat_options)
        else:
            self.res_limits[column] = chosen

    def update_air(self, column, range):
        self.air_limits[column] = range

    def update_res(self, column, range):
        self.res_limits[column] = range


def filter_data(geojson_feat, filter, bounds=[[-100, -100], [100, 100]]):  # -73.9778886, 40.7635365
    T_start = time.perf_counter()
    List = []
    for data in geojson_feat:
        conditions = [
            data['geometry']['coordinates'][0] >= bounds[0][1],
            data['geometry']['coordinates'][1] >= bounds[0][0],
            data['geometry']['coordinates'][0] <= bounds[1][1],
            data['geometry']['coordinates'][1] <= bounds[1][0]
        ]
        for k, v in filter:
            if len(v) != 0:
                if not isinstance(v[0], str):
                    conditions.extend([data['properties'][k] >= v[0], data['properties'][k] <= v[1]])
                else:
                    conditions.extend([data['properties'][k] in v])
            else:
                conditions.extend([data['properties'][k] in v])
        if all(conditions):
            List.append(data)
    print("Time it took to filter: {}".format(time.perf_counter() - T_start))
    return List


def N_airbnbs(Map_data, bounds):  # Calculate amount of airbnbs in region
    N_air = len(filter_data(Map_data.geojson_air['features'], Map_data.Filter_class.air_limits.items(), bounds))
    Price_Air = filter_data(Map_data.geojson_air['features'], Map_data.Filter_class.air_limits.items(), bounds)

    s_price = []
    s_servfee = []
    for i in range(0,len(Price_Air)):
        Int_dict = Price_Air[i].get('properties')
        Price = Int_dict.get('price')
        Serv_fee = Int_dict.get('service_fee')
        s_price.append(Price)
        s_servfee.append(Serv_fee)

    Mean_price = round(sum(s_price)/i, 1)
    Mean_servfee = round(sum(s_servfee)/i, 1)

    return N_air, Mean_price, Mean_servfee


def import_restaurants():  # importing the restaurant data
    data = pd.read_csv('RestaurantsNew.csv')
    data = data[1:5000]
    data = data[data['lon'].notna()]
    data = data[data['lat'].notna()]
    data.dropna()
    data = data.drop_duplicates(subset=['lon', 'lat'], keep='last')
    data = data.drop_duplicates(keep='last')
    data.columns = data.columns.str.replace(' ', '_')
    data['SCORE'] = data['SCORE'].fillna(0)
    data['SCORE'].astype(int)
    # Restaurants with pending grades are all put under the U for unknown so that they can be removed easily
    data['GRADE'] = data['GRADE'].fillna('U')
    data['GRADE'] = data['GRADE'].replace({'Not Yet Graded': 'U'})
    data['GRADE'] = data['GRADE'].replace({'P': 'U'})
    data['GRADE'] = data['GRADE'].replace({'Z': 'U'})
    data['SCORE'] = data['SCORE'].replace({-1: 0})
    # Under column Action, the values are made clearer
    data['ACTION'] = data['ACTION'].replace({'Violations were cited in the following area(s).': 'Violation'})
    data['ACTION'] = data['ACTION'].replace({
                                                'Establishment Closed by DOHMH.  Violations were cited in the following area(s) and those requiring immediate action were addressed.': 'Establishment Closed by DOHMH'})
    data['ACTION'] = data['ACTION'].replace(
        {'No violations were recorded at the time of this inspection.': 'No Violations'})
    data = data[data['ACTION'] != 'null']
    data = data[data['GRADE'] != 'U']

    return data


def import_airbnb():
    data = pd.read_csv('airbnb_open_data.csv', dtype={'instant_bookable': str})  # importing the airbnb Data
    data = data[1:5000]  # Line only for testing to save time
    data = data[data['long'].notna()]
    data = data[data['lat'].notna()]

    # Removing true duplicated for geographical position lat & long:
    columns = ['lat', 'long', 'service fee', 'NAME', 'host name']
    data = data.drop_duplicates(subset=columns)
    data = data.replace(np.nan, 30)
    data.dropna()

    # Replacing instant_bookable values TRUE and FALSE to YES and NO
    data['instant_bookable'] = data['instant_bookable'].replace({'FALSE': 'NO'})
    data['instant_bookable'] = data['instant_bookable'].replace({'TRUE': 'YES'})

    # Replacing the dollar sign. Changing fee to float and removing dollar sign price
    data['service fee'][data['service fee'].notnull()] = data['service fee'][data['service fee'].notnull()] \
        .replace("[$,]", "", regex=True).astype(float)
    data['price'][data['price'].notnull()] = data['price'][data['price'].notnull()] \
        .replace("[$,]", "", regex=True).astype(float)

    # Removing duplicated for the ID column:
    data = data.drop_duplicates(subset='id')

    # Removal of outliers (Based on sources)
    data = data[data['minimum nights'] < 90]
    data = data[data['Construction year'] > 2002]
    data = data[data['host_identity_verified'] != 30]
    data = data[data['neighbourhood group'] != 30]
    data = data[data['cancellation_policy'] != 30]
    data = data[data['instant_bookable'] != 30]

    # Adding a column for legality warning (Based on sources)
    query = (data['minimum nights'] <= 30.0) & (data['room type'] == 'Entire home/apt')
    data['legality'] = query
    data['legality'] = data['legality'].replace({True: 'Possible Breach'})
    data['legality'] = data['legality'].replace({False: 'No Breach'})

    data.columns = data.columns.str.replace(' ', '_')
    return data


def df_to_geojson(df, long):  # convert pandas dataframe to geojson
    print("Start Converting to geojson", end="\r\r")
    T_start = time.perf_counter()  # start timer
    dicts = df.to_dict('rows')
    geojson = dlx.dicts_to_geojson(dicts, lon=long)  # convert to geojson
    print("Time elapsed to convert to geojson: {}s".format(time.perf_counter() - T_start))
    return geojson


def get_house_data(feature):  # Create the html data for house icon on restaurant map
    features = [dict(name=feature['properties']['NAME'], lat=feature['geometry']['coordinates'][1],
                     lon=feature['geometry']['coordinates'][0])]
    # Generate geojson with a marker for each country and name as tooltip.
    # print(features)
    geojsonhouse = dlx.dicts_to_geojson([{**feat, **dict(tooltip=feat['name'])} for feat in features])
    draw_flag = assign("""function(feature, latlng){
	const flag = L.icon({iconUrl: `https://www.shareicon.net/download/2015/12/20/690629_home_512x512.png`, iconSize: [70, 60]});
	return L.marker(latlng, {icon: flag});
	}""")
    # https://i.pinimg.com/originals/b3/cc/d5/b3ccd57b054a73af1a0d281265b54ec8.jpg
    geojson_data = dl.GeoJSON(data=geojsonhouse, options=dict(pointToLayer=draw_flag), zoomToBounds=False)
    return geojson_data


class Map():
    """docstring for Map"""

    def __init__(self):
        self.df_res = import_restaurants()
        self.df_air = import_airbnb()
        self.res_col = self.df_res['GRADE'].value_counts().rename_axis('Grade').to_frame(
            'counts')  # Creating extra dataframe for grades frequencies.
        self.geojson_res = df_to_geojson(self.df_res, 'lon')
        self.geojson_air = df_to_geojson(self.df_air, 'long')

        self.Filter_class = filtering_limits(self.df_air, self.df_res)
        self.url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'  # The style of the map
        self.attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '  # Add reference to the styling of the map
        self.Data = copy.deepcopy(self.geojson_res)
        self.Show = "Restaurants"
        self.filter = assign("function(feature, context){{return true;}}")
        map_data = self.update()

        # Initial polygon creation for the minimap
        polygon = dl.Polygon(color="#ff7800", weight=1,
                             positions=[[40.43963107298772, -74.21127319335939], [40.43963107298772, -73.7889862060547],
                                        [40.95967830900992, -73.7889862060547],
                                        [40.95967830900992, -74.21127319335939],
                                        [40.43963107298772, -74.21127319335939]])
        patterns = [dict(offset='0', repeat='10', dash=dict(pixelSize=0))]
        self.inner_ring = dl.PolylineDecorator(children=polygon, patterns=patterns)

        imp_list = html.Ul(id='list', children=[html.Li('Make the cluster colours equiluminance'), html.Li(
            'Be able to select Airbnbs to maintain within the restaurant graph.'),
                                                html.Li('Visually separate the selected datapoints on the map')])
        # Creation of the html div for the entire middle part.
        self.html_div = [
            html.Div(
                id='map_div',
                style={'display': 'block'},
                className="graph_card",
                children=[
                    dl.Map(children=[
                        dl.TileLayer(url=self.url, maxZoom=20, attribution=self.attribution),
                        self.inner_ring
                        # dl.GestureHandling(),#Adds ctrl to zoom,
                    ], center=(40.7, -74), zoom=8,
                        style={'border-width': '5px', 'border-style': 'solid', 'border-color': '#f9f9f9', 'top': "80%",
                               'width': '20%', 'height': '20%', 'display': 'inline-block', 'position': 'absolute',
                               'z-index': '1000'}, id='mini-map'),

                    dl.Map(children=[
                        dl.TileLayer(url=self.url, maxZoom=20, minZoom=10, attribution=self.attribution),
                        # dl.GestureHandling(),#Adds ctrl to zoom
                        dl.GeoJSON(data=self.Data, cluster=True, id="markers", zoomToBoundsOnClick=True,
                                   superClusterOptions={"radius": 400, "minPoints": 20},
                                   children=[html.Div(id='hide_tooltip', children=[dl.Tooltip(id="tooltip")])]),
                    ], center=(40.7, -74), zoom=11,
                        style={'width': '100%', 'height': '100%', 'display': 'inline-block', 'position': 'absolute',
                               'z-index': '2'}, id='map'),
                    # html.H6('Switch', id='btn-switch'),
                    html.Div(className='btn-wrapper', children=[
                        html.Button('Show Airbnbs', id='btn-switch', n_clicks=0,
                                    style={'border-color': 'black', 'color': 'black', 'z-index': '3'}),
                    ]),
                    create_popover("Improvements", "Filter improvements", imp_list,
                                   style_button={'border-color': 'black', 'color': 'black', 'z-index': '3'},
                                   id_text='impr_map'),
                ],
            ),
            html.Div(
                id='adv_ctrl_div',
                style={'Display': 'none'},
                className="graph_card",
                children=self.get_adv_graphs()
            )
        ]

    # Switch from restaurant to airbnb map
    def switch(self):
        if self.Show == "Restaurants":
            self.Data = copy.copy(self.geojson_air)
            self.Show = "Airbnbs"
            self.url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
            self.attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '
        else:
            self.Data = copy.copy(self.geojson_res)
            self.Show = "Restaurants"
            self.url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
            self.attribution = False
        return self.update()

    # Get the html of the map
    def update(self):
        if self.Show == 'Restaurants':
            self.Data['features'] = filter_data(self.geojson_res['features'], self.Filter_class.res_limits.items())

        else:
            self.Data['features'] = filter_data(self.geojson_air['features'], self.Filter_class.air_limits.items())
        return [
            dl.TileLayer(url=self.url, maxZoom=20, minZoom=10, attribution=self.attribution),
            # dl.GestureHandling(),#Adds ctrl to zoom
            dl.GeoJSON(data=self.Data, cluster=True, id="markers", zoomToBoundsOnClick=True,
                       superClusterOptions={"radius": 400, "minPoints": 20},
                       children=[html.Div(id='hide_tooltip', children=[dl.Tooltip(id="tooltip")])]), ]

    # Update the minimap polygon returns html for the entire minimap
    def update_bounds_mini(self, bounds):
        polygon = dl.Polygon(color="#ff7800", weight=1,
                             positions=[[bounds[0][0], bounds[0][1]], [bounds[0][0], bounds[1][1]],
                                        [bounds[1][0], bounds[1][1]],
                                        [bounds[1][0], bounds[0][1]], [bounds[0][0], bounds[0][1]]])
        patterns = [dict(offset='0', repeat='10', dash=dict(pixelSize=0))]
        self.inner_ring = dl.PolylineDecorator(children=polygon, patterns=patterns)
        return [dl.TileLayer(url=self.url, maxZoom=20, attribution=self.attribution),
                self.inner_ring]

    def get_adv_graphs(self):
        imp_list_pcp = html.Ul(children=[
            html.Li('Improvement 1'),
            html.Li('Improvement 1'),
            html.Li('Improvement 1')])

        imp_list_dens = html.Ul(children=[
            html.Li('The "airbnb in visible region" maintains the viewport of the normal map not the density map.'),
            html.Li('Improvement 1'),
            html.Li('Improvement 1')])

        return [dcc.Graph(figure=self.get_fig_pcp(), id='pcp_id', style={'height': '50vh'}),
                dcc.Graph(figure=self.get_fig_map(), id='density_map', style={'height': '50vh'}),
                create_popover("Improvements", "Filter improvements", imp_list_pcp,
                               style_button={'border-color': 'black', 'color': 'black', 'z-index': '10000'},
                               id_text='impr_pcp'),
                create_popover("Improvements", "Filter improvements", imp_list_dens,
                               style_button={'border-color': 'black', 'color': 'black', 'z-index': '10000'},
                               id_text='impr_dens'), ]

    def get_fig_pcp(self):
        df_interest = self.df_air[self.Filter_class.air_columns]

        fig = go.Figure(data=
        go.Parcoords(
            line=dict(color=df_interest['price'],
                      colorscale=px.colors.sequential.algae, # Using green shades as it is best for humans
                      showscale=True,
                      cmin=1200,
                      cmax=30),
            dimensions=list([
                dict(range=[min(df_interest['price']), max(df_interest['price'])],
                     tickvals=[30, 300, 600, 900, 1200],
                     constraintrange=[self.Filter_class.air_limits['price'][0],
                                      self.Filter_class.air_limits['price'][1]],
                     label='Price', values=df_interest['price']),

                dict(range=[min(df_interest['service_fee']), max(df_interest['service_fee'])],
                     tickvals=[10, 60, 120, 180, 240],
                     constraintrange=[self.Filter_class.air_limits['service_fee'][0],
                                      self.Filter_class.air_limits['service_fee'][1]],
                     label='Service Fee', values=df_interest['service_fee']),

                dict(constraintrange=[self.Filter_class.air_limits['minimum_nights'][0],
                                      self.Filter_class.air_limits['minimum_nights'][1]],
                     range=[0, max(df_interest['minimum_nights'])],
                     tickvals=[0, 45, 90],
                     label='Minimum Nights', values=df_interest['minimum_nights']),

                dict(constraintrange=[self.Filter_class.air_limits['Construction_year'][0],
                                      self.Filter_class.air_limits['Construction_year'][1]],
                     range=[2002, max(df_interest['Construction_year'])],
                     tickvals=[2002, 2008, 2012, 2016, 2022],
                     label='Construction Year', values=df_interest['Construction_year']),

                dict(constraintrange=[self.Filter_class.air_limits['number_of_reviews'][0],
                                      self.Filter_class.air_limits['number_of_reviews'][1]],
                     range=[0, max(df_interest['number_of_reviews'])],
                     label='Number of Reviews', values=df_interest['number_of_reviews'])
            ])
        )
        )

        # Added opacity as explained in the lecture to ease readibility of the PCP and using pop out for ticks on the PCP.
        fig.update_traces(unselected_line_opacity=0.01, selector=dict(type='parcoords'),
                          tickfont=dict(family='Arial', size=12, color='purple'))

        # Setting a very light grey background so that the white on the colorcale is better visible
        fig.update_layout(
            paper_bgcolor='hsla(186, 0%, 88%, 0.58)', uirevision='0'
        )

        return fig

    def get_fig_map(self):
        self.Data['features'] = filter_data(self.geojson_air['features'], self.Filter_class.air_limits.items())
        data = self.geojson_to_df(copy.copy(self.Data))
        fig = px.density_mapbox(data, lat='lat', lon='long', opacity=0.6, radius=15,
                                center=dict(lat=40.7, lon=-74), zoom=8,
                                mapbox_style="open-street-map",
                                custom_data = ['properties.price', 'properties.room_type', 'properties.legality'])
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, uirevision='0')
        fig.update_traces(hovertemplate='Latitude: %{lat} <br>Longitude: %{lon} <br>Price: %{customdata[0]} <br>Room Type: %{customdata[1]} <br>Legality Warning: %{customdata[2]}')
        return fig

    def geojson_to_df(self, data):
        T_start = time.perf_counter()
        df = pd.json_normalize(data["features"])
        coords = 'geometry.coordinates'
        df[['long', 'lat']] = pd.DataFrame(df[coords].tolist(), columns=['long', 'lat'])
        print("Time elapsed to convert to df: {}".format(time.perf_counter() - T_start))
        return df

