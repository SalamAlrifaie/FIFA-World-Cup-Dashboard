import pandas as pd 
from dash import dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px

data = [
    [1930, "Uruguay", "Argentina", "4–2"],
    [1934, "Italy", "Czechoslovakia", "2–1 (a.e.t.)"],
    [1938, "Italy", "Hungary", "4–2"],
    [1950, "Uruguay", "Brazil", "2–1"],
    [1954, "Germany", "Hungary", "3–2"],
    [1958, "Brazil", "Sweden", "5–2"],
    [1962, "Brazil", "Czechoslovakia", "3–1"],
    [1966, "England", "Germany", "4–2 (a.e.t.)"],
    [1970, "Brazil", "Italy", "4–1"],
    [1974, "Germany", "Netherlands", "2–1"],
    [1978, "Argentina", "Netherlands", "3–1 (a.e.t.)"],
    [1982, "Italy", "Germany", "3–1"],
    [1986, "Argentina", "Germany", "3–2 (a.e.t.)"],
    [1990, "Germany", "Argentina", "1–0"],
    [1994, "Brazil", "Italy", "0–0 (a.e.t.) (3–2 p)"],
    [1998, "France", "Brazil", "3–0"],
    [2002, "Brazil", "Germany", "2–0"],
    [2006, "Italy", "France", "1–1 (a.e.t.) (5–3 p)"],
    [2010, "Spain", "Netherlands", "1–0 (a.e.t.)"],
    [2014, "Germany", "Argentina", "1–0 (a.e.t.)"],
    [2018, "France", "Croatia", "4–2"],
    [2022, "Argentina", "France", "3–3 (a.e.t.) (4–2 p)"]
]

coordinates = {
    "Country": ["Brazil", "Germany", "Italy", "Argentina", "France", "Uruguay", "England", "Spain"],
    "ISO": ["BRA", "DEU", "ITA", "ARG", "FRA", "URY", "GBR", "ESP"],
    "lat": [-14.235, 51.1657, 41.8719, -38.4161, 46.2276, -32.5228, 52.3555, 40.4637],
    "lon": [-51.9253, 10.4515, 12.5674, -63.6167, 2.2137, -55.7658, -1.1743, -3.7492]
}

wins = {
    "Country": ["Brazil", "Germany", "Italy", "Argentina", "France", "Uruguay", "England", "Spain"],
    "ISO": ["BRA", "DEU", "ITA", "ARG", "FRA", "URY", "GBR", "ESP"],
    "Wins": [5, 4, 4, 3, 2, 2, 1, 1]
}

df = pd.DataFrame(data, columns=["Year", "Winner", "Runner-Up", "Score"])
coordinates_df = pd.DataFrame(coordinates)
wins_df = pd.DataFrame(wins)
wins_df = pd.merge(wins_df, coordinates_df, on=['Country', 'ISO'])

df.to_csv("world_cup_data.csv", index=False)
wins_df.to_csv("world_cup_wins.csv", index=False)

data_df = pd.read_csv('world_cup_data.csv')
wins_df = pd.read_csv('world_cup_wins.csv')

data_df['Year'] = data_df['Year'].astype(int)


# Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# process the data
years = sorted(data_df['Year'].unique(), reverse=True)
winning_countries = sorted(wins_df['Country'].unique())

app.layout = dbc.Container([
    html.H1("FIFA Soccer World Cup History", className='mb-4 text-center'),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4("Choropleth Map", className='text-center'),
                dcc.Graph(id='choropleth-map')
            ], className='mb-4')
        ], width=8),
        
        dbc.Col([
            html.Div([
                
                html.H5("Select a Country:", className='mt-3'),
                dcc.Dropdown(id='country-selector', options=[{'label': i, 'value': i} for i in winning_countries], placeholder='Select a country to view'),
                html.Div(id='country-wins-display', className='mt-3'),
                

                html.Hr(),
                

                html.H5("Select a Year:", className='mt-3'),
                dcc.Dropdown(id='year-selector', options=[{'label': str(y), 'value': y} for y in years], placeholder='Select a year to view summary'),
                html.Div(id='year-summary-display', className='mt-3'),
                
                
                html.Hr(),
                

                html.H4("All countries that ever won a World Cup:", className='mt-3'),
                html.Div(id='winners-list', className='mb-3'),

            ], style={'position': 'sticky', 'top': '20px'})
        ], width=4)
    ])
], fluid=True)

# map callback
@app.callback(
    Output('choropleth-map', 'figure'),
    Input('country-selector', 'value')
)

def update_map(selected_country):

    fig = px.choropleth(wins_df, locations="ISO", color="Wins", hover_name="Country", color_continuous_scale='Purples', range_color=(0, wins_df['Wins'].max()), labels={'Wins': 'World Cup Wins'}, custom_data=['Country', 'Wins'])
    
    fig.add_scattergeo(locations=wins_df['ISO'],
        hovertext=wins_df.apply(lambda x: f"{x['Country']}<br>World Cup Wins: {x['Wins']}", axis=1),
        mode='markers',
        marker=dict(size=35,color='rgba(0,0,0,0)',line=dict(width=0)),
        hoverinfo='text',
        showlegend=False
    )
    
    # country labels
    fig.add_scattergeo(locations=coordinates_df['ISO'], text=coordinates_df['Country'], mode='text',
        textfont=dict(size=11, color='black', family='Arial', weight='bold'),
        hoverinfo='none', showlegend=False
    )
    
    # zoom on select
    if selected_country:
        country_coords = coordinates_df[coordinates_df['Country'] == selected_country]
        
        if not country_coords.empty:
            lat = country_coords['lat'].iloc[0]
            lon = country_coords['lon'].iloc[0]
            fig.update_geos(center={"lat": lat, "lon": lon}, projection_scale=3, visible=True, landcolor='rgb(207, 207, 207)', countrycolor='rgb(205, 205, 205)')
    
    else:
        fig.update_geos(center=None, projection_scale=1, visible=True)

    # layout updates
    fig.update_layout(
        geo=dict(showframe=False,
            showcoastlines=False,
            showcountries=True,
            countrycolor='rgb(150, 150, 165)',
            subunitcolor='rgb(200, 200, 200)',
            projection_type='equirectangular',
            landcolor='rgb(240, 240, 242)',
            bgcolor='rgba(255,255,255,0.1)'
        ),
        margin={"r":100, "t":20, "l":0, "b":0},
        coloraxis_colorbar=dict(title='World Cup Wins', x=1.0, y=0.5, len=0.9, thickness=28, title_side='top'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# winner list callback
@callback(
        Output('winners-list', 'children'), 
        Input('choropleth-map', 'clickData')
)

def show_winners(_):
    return html.Ul([html.Li(w) for w in winning_countries])


# wins selector callback
@callback(
        Output('country-wins-display', 'children'), 
        Input('country-selector', 'value')
)

def show_country_wins(country):
    if not country:
        return ""
    
    wins = wins_df[wins_df['Country'] == country]['Wins'].values[0]
    return html.Div([
        html.H5(f"{country} World Cup Wins:"),
        html.H2(f"{wins}", style={'color': '#3F007D'})
    ])


# year selector callback
@callback(
        Output('year-summary-display', 'children'),
        Input('year-selector', 'value')
)

def show_year_summary(year):
    if not year:
        return ""
    
    try:
        data = data_df[data_df['Year'] == year].iloc[0]
        return html.Div([
            html.H5(f"{year} World Cup Summary:"),
            html.P(f"Winner: {data['Winner']}"),
            html.P(f"Runner-Up: {data['Runner-Up']}"),
            html.P(f"Score: {data['Score']}")
        ])
    
    except IndexError:
        return html.Div("No data available for this year", style={'color': 'red'})

if __name__ == '__main__':
    app.run(debug=True, port=8053)
