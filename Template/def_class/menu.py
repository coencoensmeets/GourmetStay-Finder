from dash import dcc, html
import plotly.express as px

# Generate figures
def range_slider(df, column):
	fig = px.histogram(df, x=column, nbins=20, marginal="violin")
	fig.update_layout(
		xaxis=dict(
			rangeslider=dict(
				visible=True,
			)
		),
		height=200,
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
			html.H5("Visualisation tool"),
			html.H4("Group 44"),
			html.Div(
				className="intro",
				children="This is a work in progress",
			),
			# html.H3("Test", id='bounds')
		],
	)

def generate_control_card(html_filtering):
	return html.Div(
		id="control-card",
		children=[
			html.Hr(),
			html.H4("Controls"),
			*html_filtering,
			html.Div(className='btn-wrapper',children=[
					html.Button('Advanced', id='btn-controls', n_clicks=0),
				])
		], style={"textAlign": "float-left"}
	)


def make_menu_layout(Map_data):
	html_filtering = [html.Div(children='Airbnb filtering'),
				dcc.Dropdown(Map_data.Filter_class.air_columns, Map_data.Filter_class.air_columns[0], clearable=False, id='air_filter_drop'),
				dcc.Graph(figure=range_slider(Map_data.df_air, Map_data.Filter_class.air_columns[0]), id='air_filter_graph'),
				html.Div(children='Restaurant filtering'),
				dcc.Dropdown(Map_data.Filter_class.res_columns, Map_data.Filter_class.res_columns[0], clearable=False, id='res_filter_drop'),
				dcc.Graph(figure=range_slider(Map_data.df_res, Map_data.Filter_class.res_columns[0]), id='res_filter_graph'),
				html.Div(children='CATEGORICAL FILTERING'),
				html.Div(children='AIRBNBs'),
				dcc.Dropdown(Map_data.Filter_class.air_cat_columns, id='cat_air_drop'),
				dcc.Checklist(id='cat_air_checklist'),
				html.Button(id='air_reset_button', n_clicks=0, children='Reset Filter for AIRBNBs'),
				html.Div(id='air_cat_on', children='AIRBNB Categorical filtering OFF'),
				html.Div(children='RESTAURANTS'),
				dcc.Dropdown(Map_data.Filter_class.res_cat_columns, id='cat_res_drop'),
				dcc.Checklist(id='cat_res_checklist'),
				html.Button(id='res_reset_button', n_clicks=0, children='Reset Filter for RESTAURANTS'),
				html.Div(id='res_cat_on', children='RESTAURANT Categorical filtering OFF')]
	return [generate_description_card(), generate_control_card(html_filtering)]
