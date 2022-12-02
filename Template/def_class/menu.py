from dash import dcc, html


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
            html.H4("Controls")
        ], style={"textAlign": "float-left"}
    )


def make_menu_layout():
    return [generate_description_card(), generate_control_card()]
