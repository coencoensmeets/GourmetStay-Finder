from dash import dcc, html


def generate_description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Visualisation tool"),
            html.H4("Group 44"),
            html.Div(
                id="intro",
                children="This is a work in progress",
            ),
        ],
    )


def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.Hr
            html.H4("Controls")
        ], style={"textAlign": "float-left"}
    )


def make_menu_layout():
    return [generate_description_card(), generate_control_card()]
