from dash import dcc, html

def generate_output_top():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        children=[
            html.H5("CURRENTLY SHOWING:"),
            html.H4("", id='data_showing'),
            # html.Button('Button 1', id='btn-1', n_clicks=0),
        ],
    )


def generate_output():
    return html.Div(
        children=[
            html.Hr(style = {'height':'2px', 'border-width':'0', 'color':'gray', 'background-color':'gray'}),
            #Restaurant Data
            html.Div(id='Information_hover'),
            html.Hr(),
            html.Div(id='Information_click'),
            html.Hr(style = {'height':'2px', 'border-width':'0', 'color':'gray', 'background-color':'gray'}),
            html.H5("AIRBNBs in the visible region:"),
            html.Div(
            children=[
            	html.Div(id='Nairbnb',children='Number of AIRBNBs:'),
                html.Hr(style={'width': '0%'}),
                html.Div(id='meanprice', children='Average Price:'),
                html.Hr(style={'width': '0%'}),
                html.Div(id='meanservice', children ='Average Service Fee:')
            ]
            ),
			dcc.Loading(
			id="loading-1",
            type="default",
            children=html.Div(id="loading-output")
        	),

        ], style={"textAlign": "float-left"}
    )


def make_output_layout():
    return [generate_output_top(), generate_output()]