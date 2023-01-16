from dash import dcc, html


<<<<<<< Updated upstream
=======


# Generate HTML CODE:
>>>>>>> Stashed changes
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


def generate_control_card():
    return html.Div(
        id="control-card",
        children=[
            html.Hr(),
            html.H4("Controls"),
            html.Div(className='btn-wrapper',children=[
                    html.Button('Advanced', id='btn-controls', n_clicks=0),
                ])
        ], style={"textAlign": "float-left"}
    )

<<<<<<< Updated upstream
=======
def make_menu_layout(Map_data):
	html_filtering = [html.Div(children='Airbnb filtering'),
				dcc.Dropdown(Map_data.Filter_class.air_columns, Map_data.Filter_class.air_columns[0], clearable=False, id='air_filter_drop'),
				dcc.Graph(figure=range_slider(Map_data.df_air, Map_data.Filter_class.air_columns[0]), id='air_filter_graph'),
				html.Div(children='Restaurant filtering'),
				dcc.Dropdown(Map_data.Filter_class.res_columns, Map_data.Filter_class.res_columns[0], clearable=False, id='res_filter_drop'),
				dcc.Graph(figure=range_slider(Map_data.df_res, Map_data.Filter_class.res_columns[0]), id='res_filter_graph'),
				html.Div(children='CATEGORICAL FILTERING'),
				dcc.Dropdown(Map_data.Cat_Filter_class.air_cat_columns, id='cat_air_drop'),
				dcc.Checklist(id='cat_air_checklist'),
				html.Button(id='reset_button',n_clicks=0,children ='Reset Filter'),
				html.Div(id= 'air_cat_on', children ='Categorical filters OFF')]

>>>>>>> Stashed changes

def make_menu_layout():
    return [generate_description_card(), generate_control_card()]
