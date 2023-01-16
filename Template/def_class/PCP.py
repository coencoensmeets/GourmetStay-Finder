from Middle import import_airbnb

import Middle
import plotly.express as px
import plotly.graph_objects as go

df = import_airbnb()

air_columns = ['price', 'service_fee', 'minimum_nights','Construction_year', 'number_of_reviews']
df_interest = df[air_columns]


# Changing dates close to 0 years to 2000 and showing that as unknown in the plot.
# There is no data point at 2000 so it can be safely used.
df_interest['Construction_year'].mask((df_interest['Construction_year'] < 2000), inplace=True)
df_interest['Construction_year'] = df_interest['Construction_year'].fillna(2000)

# Same solution used for minimum nights
df_interest['minimum_nights'].mask((df_interest['minimum_nights'] < 0), inplace=True)
df_interest['minimum_nights'] = df_interest['minimum_nights'].fillna(6000)



fig = go.Figure(data=
    go.Parcoords(
        line = dict(color = df_interest['price'],
                   colorscale =px.colors.sequential.algae,
                   showscale = True,
                   cmin = 1200,
                   cmax = 30),
        dimensions = list([
            dict(constraintrange = [1,150],
                 label = 'Price', values = df_interest['price']),
            dict(label = 'Service Fee', values = df_interest['service_fee']),
            dict(range = [0, 6000],
                 # Option to create Unknown on the plot for the user
                 tickvals = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000],
                 ticktext = ['0', '500', '1000', '1500', '2000', '2500', '3000', '3500', '4000', '4500', '5000', '5500', 'Unknown'],
                 label = 'Minimum Nights', values = df_interest['minimum_nights']),
            dict(range = [2000, max(df_interest['Construction_year'])],
                 tickvals = [2000, 2002, 2004, 2006, 2010, 2012, 2014, 2016, 2018, 2020, 2022],
                 ticktext = ['Unknown', '2002', '2004', '2006', '2010', '2012', '2014', '2016', '2018', '2020', '2022'],
                 label = 'Construction Year', values = df_interest['Construction_year']),
            dict(range = [0, max(df_interest['number_of_reviews'])],
                label = 'Number of Reviews', values = df_interest['number_of_reviews'])
        ])
    )
)

# Added opacity as explained in the lecture to ease readibility
fig.update_traces(unselected_line_opacity=0.01, selector=dict(type='parcoords'),
                  )

# Setting a very light grey background so that the white on the colorcale is better visible
fig.update_layout(
    paper_bgcolor = 'hsla(186, 0%, 88%, 0.58)'
)

fig.show()


