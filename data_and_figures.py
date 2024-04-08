import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

def create_site_dataframe(site_filepath='data/groundwater_level_sites.csv'):
    """Create df from site_data csv file. Return cleaned df with 
    'SITE_CODE', 'GSA_NAME', 'SMC_MT', 'LATITUDE', 'LONGITUDE'. 
    Include only sites that contain a minimal threshold value."""
    site_df = pd.read_csv(site_filepath)
    site_df = site_df[['SITE_CODE', 'GSA_NAME', 'SMC_MT', 'LATITUDE', 'LONGITUDE']].copy()
    site_df = site_df[site_df['SMC_MT'].notna()]
    return site_df

def create_measurements_dataframe(measurements_filepath='data/measurements.csv'):
    """Create dataframe from measurements.csv. Only include
    'site_code', 'msmt_date', 'gwe' features."""
    measurements_df = pd.read_csv(measurements_filepath, low_memory=False)
    measurements_df = measurements_df[['site_code', 'msmt_date', 'gwe']].copy()
    return measurements_df

def create_merged_data(site_df, measurements_df):
    """Join measurement and site data on site code"""
    merged_df = pd.merge(site_df, measurements_df, left_on='SITE_CODE', right_on='site_code', how='inner')
    return merged_df

def map_figure_data(merged_df):
    """Pre-process data for map figure.
    Filter data to include most recent GWE measurement for each site.
    Create new column, 'status' to indicate if GWE is above or below MT"""
    # Only data w/ gwe measurement
    df = merged_df[merged_df['gwe'].notnull()].copy()  
    df['msmt_date'] = pd.to_datetime(df['msmt_date'])  # Convert 'msmt_date' to datetime
    
    # Filter the DataFrame to keep only the most recent measurements for each 'site_code'
    idx = df.groupby('site_code')['msmt_date'].idxmax()
    recent_gwe = df.loc[idx]

    # Determine the status (GWE above/below minimal threshold)
    recent_gwe['status'] = recent_gwe.apply(lambda row: "Above Minimum Threshold" if row['gwe'] > row['SMC_MT'] else "Below Minimum Threshold", axis=1)
    recent_gwe['msmt_date'] = recent_gwe['msmt_date'].dt.date  # Conver to just date, not time

    return recent_gwe

def map_figure(recent_gwe):
    """Create Map Figure of most recent GWE measurements, 
    color coded by threshold status."""
    # Define initial map figure
    fig = px.scatter_mapbox(recent_gwe,
                        lat='LATITUDE',
                        lon='LONGITUDE',
                        color='status',  # Color code by status
                        custom_data=['SITE_CODE', 'GSA_NAME', 'gwe', 'SMC_MT', 'msmt_date'],
                        hover_name='GSA_NAME',
                        hover_data={'gwe', 'SMC_MT', 'msmt_date'},
                        title='GWE Measurements per GSA')

    # Centering on California
    fig.update_layout(legend_title_text='GWE Status',
                    mapbox_style="open-street-map",
                    mapbox={"center": {"lat": 36.7783, "lon": -119.4179}, "zoom": 4.5},
                    margin={"r":0,"t":0,"l":0,"b":0})

    # Customize Hover Data
    fig.update_traces(hovertemplate="<br>".join([
        "<b>%{hovertext}\n</b>",
        "GWE: %{customdata[2]} ft",
        "SMC_MT: %{customdata[3]} ft",
        "Measurement Date: %{customdata[4]}"]),
        showlegend = True)

    # Add title to graph
    fig.update_layout(
        title={
            'text': "GWE Measurements per GSA",
            'y':0.95,
            'x':0,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': dict(
                family="Arial, sans-serif",
                size=20,
                color="black"
            )
        },
        margin={"t": 50}
    )
    return fig


def hitoric_site_data(site_code, merged_df):
    """Filters merged_df by site, and outputs sorted data from specific site_code, 
    and minimal threshold for that site. Prepares data for historic GWE plot."""
    df_site = merged_df[merged_df['SITE_CODE'] == site_code].copy()  # Filters data by site
    df_site['msmt_date'] = pd.to_datetime(df_site['msmt_date'])  # Convert to datetime
    df_site_sorted = df_site.sort_values(by='msmt_date')  # Sort by date

    # Minimal threshold of site
    smc_mt = df_site_sorted['SMC_MT'].mean()  # Calculate MT

    return df_site_sorted, smc_mt


def historic_gwe_figure(df_site_sorted, site_name, smc_mt):
    """Create line plot of historic GWE measurements given site. 
    Include minimal threshold of site."""
    fig = go.Figure()
    
    # Historic GWE Data
    fig.add_trace(go.Scatter(x=df_site_sorted['msmt_date'], y=df_site_sorted['gwe'],
                                    mode='lines+markers',
                                    name='GWE',
                                    marker_color='navy'))

    # Minimal Threshold Line
    fig.add_hline(y=smc_mt, line=dict(color='red', width=2, dash='dash'),
                        annotation_text=f"MT: {smc_mt:.2f}",
                        annotation_position="bottom right")

    fig.update_layout(title=f'{site_name} Groundwater Elevation (GWE) Over Time',
                            xaxis_title='Date',
                            yaxis_title='Groundwater Elevation (GWE)',
                            xaxis=dict(
                                tickformat="%Y-%m-%d",
                                nticks=20,
                                tickangle=45
                            ),
                            yaxis=dict(
                                fixedrange=False
                            ))
    return fig
