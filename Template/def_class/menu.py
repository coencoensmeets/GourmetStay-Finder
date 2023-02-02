from dash import dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc
import time

def create_popover(button,header, text, style_button=None, id_text=str(time.perf_counter()).replace(".", ""), style_wrapper=None):
	popovers = html.Div(className='btn-wrapper',style=style_wrapper,
		children=[
			html.Button(
				button,
				id=id_text ,
				n_clicks=0,
				style=style_button
			),
			dbc.Popover(
				[
					dbc.PopoverHeader(header,style={'font-size': '15px'}),
					dbc.PopoverBody(text),
				],
				target=id_text ,
				trigger="focus",
				style={'z-index':'100000000','font-size': '15px'}
			),
		]
	)
	return popovers


# Generate figures
def range_slider(df, column):
	fig = px.histogram(df, x=column, nbins=20, marginal="violin")
	fig.update_layout(
		xaxis=dict(
			rangeslider=dict(
				visible=True,
			)
		),
		height=170,
		paper_bgcolor='rgba(0,0,0,0)',
    	plot_bgcolor='rgba(0,0,0,0)',
		margin=dict(l=0, r=0, t=0, b=20),
		dragmode="zoom",
    	hovermode="x",
	)
	return fig

# Generate HTML CODE:
def generate_description_card():
	return html.Div(
		id="description-card",
		children=[
			html.H5("NEW YORK MAPS JBI100 Visualization", style ={'font-weight':'bold'}),
			html.H4("Group 44", style={'font-weight':'bold','margin-bottom':'0rem'}),
			# html.Div(
			# 	className="intro",
			# 	children="This is a work in progress",
			# ),
			# html.H3("Test", id='bounds')
		],
	)

def generate_control_card(html_filtering):
	imp_list_filt = html.Ul(id='my-list', children=[html.Li('Due to Plotly limitations, the range sliders reset when switching between variables'),html.Li("The histograms don't take into account the data filtered by categorical filters"),
													html.Li('Interconnectivity of the app runs on a callback with multiple inputs, leading to multiple fires, slowing down filtering process')])

	return html.Div(
		id="control-card",
		children=[
			html.Hr(style = {'width':'100%','height':'2px', 'border-width':'0', 'color':'gray', 'background-color':'gray'}),
			html.H4("Controls"),
			*html_filtering,
			create_popover("Improvements", "Filter improvements", imp_list_filt),
			html.Hr(style = {'width':'100%','height':'2px', 'border-width':'0', 'color':'gray', 'background-color':'gray'}),
			html.H5("TOGGLE: Normal - Advanced Section"),
			html.Div('Use the Parallel Coordinate Plot (PCP) for Multivariate Filtering', style = {'font-weight':'bold', 'font-style':'italic'}),
			html.Div(className='btn-wrapper',children=[
					dbc.Button(children='Switch to Advanced Section', id='btn-controls', n_clicks=0, color ='secondary',size='lg'),
				])
		], style={"textAlign": "float-left"}
	)


def make_menu_layout(Map_data):
	html_filtering = [
				html.H5("AIRBNBS:"),
				html.Div(children='NUMERICAL FILTERS', style = {'font-weight':'bold', 'font-style':'italic'}),
				dcc.Dropdown(Map_data.Filter_class.air_columns, Map_data.Filter_class.air_columns[0], clearable=False, id='air_filter_drop'),
				dcc.Graph(figure=range_slider(Map_data.df_air, Map_data.Filter_class.air_columns[0]), id='air_filter_graph'),
				html.Hr(style={'width': '0%'}),
				html.Div(children='CATEGORICAL FILTERS', style = {'font-weight':'bold', 'font-style':'italic'}),
				dcc.Dropdown(Map_data.Filter_class.air_cat_columns, id='cat_air_drop'),
				dcc.Checklist(id='cat_air_checklist'),
				html.Div(id='air_cat_on', children='CATEGORICAL FILTERING: OFF', style={'font-style': 'italic'}),
				dbc.Button(id='air_reset_button', n_clicks=0, children='Reset Categorical', color = 'secondary', size = 'lg'),
				html.Hr(),
				html.H5('RESTAURANTS:'),
				html.Div(children='NUMERICAL FILTERS', style = {'font-weight':'bold', 'font-style':'italic'}),
				dcc.Dropdown(Map_data.Filter_class.res_columns, Map_data.Filter_class.res_columns[0], clearable=False, id='res_filter_drop'),
				dcc.Graph(figure=range_slider(Map_data.df_res, Map_data.Filter_class.res_columns[0]), id='res_filter_graph'),
				html.Hr(style={'width': '0%'}),
				html.Div(children='CATEGORICAL FILTERS', style = {'font-weight':'bold', 'font-style':'italic'}),
				dcc.Dropdown(Map_data.Filter_class.res_cat_columns, id='cat_res_drop'),
				dcc.Checklist(id='cat_res_checklist'),
				html.Div(id='res_cat_on', children='CATEGORICAL FILTERING: OFF', style={'font-style': 'italic'}),
				dbc.Button(id='res_reset_button', n_clicks=0, children='Reset Categorical', color = 'secondary', size = 'lg'),
				html.Hr()]
	return [generate_description_card(), generate_control_card(html_filtering)]
