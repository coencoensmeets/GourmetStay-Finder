from dash import dcc, html

def generate_output_top():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        children=[
            html.H5("Currently showing:"),
            html.H4("", id='data_showing'),
            # html.Button('Button 1', id='btn-1', n_clicks=0),
        ],
    )


def generate_output():
    return html.Div(
        children=[
            html.Hr(),
            #Restaurant Data
            html.Div(id='Information_hover'),
            html.Hr(),
            html.Div(id='Information_click'),
            html.Hr(),
            html.Div(
            children=[
            	html.Div(id='Nairbnb',children='Airbnbs in region: ')
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