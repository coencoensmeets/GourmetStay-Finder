import dash
from dash import dcc
from dash import html
from def_class.menu import make_menu_layout
from def_class.Map import Map


if __name__ == '__main__':
	app = dash.Dash(__name__)
	app.title = "Group 44"
	Middle = Map()
	
	app.layout = html.Div(
		id="app-container",
		children=[
			# Left column
			html.Div(

				id="left-column",
				className="two columns",
				children=make_menu_layout()
			),

			# Middle column
			html.Div(
				id="middle-column",
				className="eight columns",
				children=Middle.html_div
			),

			html.Div(

				id="right-column",
				className="two columns",
			),
		],
	)
	app.run_server(debug=True, dev_tools_ui=False)