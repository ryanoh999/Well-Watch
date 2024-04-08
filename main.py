import dash
from dash import dcc, html, Input, Output
from data_and_figures import *

# Initialize Dash app
app = dash.Dash(__name__)

# Prepare data
site_df = create_site_dataframe(site_filepath='data/groundwater_level_sites.csv')
measurements_df = create_measurements_dataframe(measurements_filepath='data/measurements.csv')
merged_df = create_merged_data(site_df, measurements_df)
recent_gwe = map_figure_data(merged_df)

# Map figure
map_fig = map_figure(recent_gwe)

# Define app
app.layout = html.Div([html.H1(children='Well Watch'),
    # Container for both plots with display set to 'flex' to align children side by side
    html.Div([
        dcc.Graph(id='location-map', figure=map_fig),
        html.Div(id='site-gwe-plot-container')  # Container for the hisotric site data plot
    ], style={'display': 'flex', 'flexDirection': 'row'})
])

@app.callback(
    Output('site-gwe-plot-container', 'children'),  # Update the container's children to show the new plot based on click
    Input('location-map', 'clickData'))

def display_site_gwe_plot(clickData):
    if clickData is None:
        # Return an empty div if no site has been clicked initially
        return html.Div()
    
    site_code = clickData['points'][0]['customdata'][0]  # Site_code from click
    site_name = clickData['points'][0]['customdata'][1]  # Site_name from click

    # Get historic data and MT of site clicked
    df_site_sorted, smc_mt = hitoric_site_data(site_code, merged_df)

    # Plot historic data and MT of site clicked
    site_fig = historic_gwe_figure(df_site_sorted, site_name, smc_mt)

    # Return a Graph component with the new figure
    return dcc.Graph(figure=site_fig)

if __name__ == '__main__':
    app.run_server(debug=True)