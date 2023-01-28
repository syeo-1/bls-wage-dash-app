from dash import Dash, dcc, html, Input, Output, State, ctx, ALL
import plotly.express as px
from dash.exceptions import PreventUpdate
import pandas as pd
import sqlite3
# import dash_bootstrap_components as dbc
import json

# check the "simple example" section here for reference: https://dash.plotly.com/clientside-callbacks

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

# TODO: search up: why global variables will break your app (in dash)
# looks like the main way to fix is by using: sharing data between callbacks

app = Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server
# app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

# create connection to the database first
conn = sqlite3.connect('wage_stats.db')

# get dataframe for the county wage data
wage_df = pd.read_sql_table('county_wage_data', 'sqlite:///wage_stats.db')

# get dataframe for the region data
region_df = pd.read_sql_table('region_data', 'sqlite:///wage_stats.db')

# get unique list of occupation titles
occupation_titles = wage_df['occupation_title'].unique()

# print(region_df.head())

# get unique list of the counties!

counties = region_df['May 2021 MSA name'].unique()

def create_job_county_list(jobs, counties):
    result = []

    for job in jobs:
        for county in counties:
            result.append(','.join([job, county]))

    return result
# print('poop')
county_jobs = create_job_county_list(occupation_titles, counties)
# print(county_jobs)


app.layout = html.Div([
    # dcc.Store(id='wage-df-dict', storage_type='local', data={
    # 'occupation_title': [],
    # 'employment': [],
    # 'employment_rse_percent': [],
    # 'employment_per_1000_jobs': [],
    # 'location_quotient': [],
    # 'median_hourly_wage_usd': [],
    # 'mean_hourly_wage_usd': [],
    # 'annual_mean_wage_usd': [],
    # 'mean_wage_rse_percent': [],
    # 'county_name': [],
    # 'msa_code': [],
    # 'msa_job': []
    # }),
    'County',
    dcc.Dropdown(counties, placeholder='type in a county!', id='county-names', ),
    'Job',
    dcc.Dropdown(occupation_titles, placeholder='type in a job!', id='occupation-titles'),
    html.Button(id='submit-button-state', n_clicks=0, children='Display Data'),
    html.Div(id='remove-graphs', children=[]),
    html.Div(id='output-state'),
    dcc.Graph(id='annual_mean_wage_usd'),
    dcc.Graph(id='hourly_median_wage_usd'),
    # create store for the dataframe to graph
    dcc.Store(id='county-job-pairs', data={
    'occupation_title': [],
    'employment': [],
    'employment_rse_percent': [],
    'employment_per_1000_jobs': [],
    'location_quotient': [],
    'median_hourly_wage_usd': [],
    'mean_hourly_wage_usd': [],
    'annual_mean_wage_usd': [],
    'mean_wage_rse_percent': [],
    'county_name': [],
    'msa_code': [],
    'msa_job': []
    }),
    # create store for values user has already entered
    dcc.Store(id='entered-county-job-pairs', data=[]) 
])

# wage_data_to_graph = {
#     'occupation_title': [],
#     'employment': [],
#     'employment_rse_percent': [],
#     'employment_per_1000_jobs': [],
#     'location_quotient': [],
#     'median_hourly_wage_usd': [],
#     'mean_hourly_wage_usd': [],
#     'annual_mean_wage_usd': [],
#     'mean_wage_rse_percent': [],
#     'county_name': [],
#     'msa_code': [],
#     'msa_job': []
# }

# need this to keep track of what user has entered in so far.
# msa_job_set = set()

# take the existing dataset that's on display in the browser
# store it in a variable inside the function
# figure out what the user has entered in as values to save
# append those new values to the dataset variable taken from the user's browser
# return the 


@app.callback(

    Output('remove-graphs', 'children'),
    Output('annual_mean_wage_usd', 'figure'),
    Output('hourly_median_wage_usd', 'figure'),
    Output('county-job-pairs', 'data'),
    Output('entered-county-job-pairs', 'data'),
              Input('submit-button-state', 'n_clicks'),
              Input({'type': 'remove-single-graph', 'index': ALL}, 'n_clicks'),
              State('remove-graphs', 'children'),
              State('county-names', 'value'),
              State('occupation-titles', 'value'),
              State('county-job-pairs', 'data'),
              State('entered-county-job-pairs', 'data'))
def update_output(n_clicks, _, children, county_name, occupation_title, county_job_dict, entered_county_job_pairs):
    '''
    update the graphs and remove buttons upon clicking the add data button
    '''
    # prevent the None callbacks so Store components are only updated when data is available
    if n_clicks is None:
        raise PreventUpdate


    if ctx.triggered_id == 'submit-button-state':
        # get the county_code (May 2021 MSA) from the region data dataframe
        msa_code = None
        for _, row in region_df.iterrows():
            if row['May 2021 MSA name'] == county_name:
                msa_code = row['May 2021 MSA code ']

        # print(msa_code)
        print(county_name, occupation_title)

        # get the row from the wage dataframe with matching msa code and occupation
        row = wage_df.loc[(wage_df['county_code'] == str(msa_code)) & (wage_df['occupation_title'] == occupation_title)]
        if not row.empty:
            if not (county_name, occupation_title) in entered_county_job_pairs:
                entered_county_job_pairs.append((county_name, occupation_title))
                # print('===')
                # print(row['employment'].values[0])
                # print(row)
                # print('===')
                county_job_dict['occupation_title'].append(occupation_title)
                county_job_dict['employment'].append(row['employment'].values[0])
                county_job_dict['employment_rse_percent'].append(row['employment_rse_percent'].values[0])
                county_job_dict['employment_per_1000_jobs'].append(row['employment_per_1000_jobs'].values[0])
                county_job_dict['location_quotient'].append(row['location_quotient'].values[0])
                county_job_dict['median_hourly_wage_usd'].append(row['median_hourly_wage_usd'].values[0])
                county_job_dict['mean_hourly_wage_usd'].append(row['mean_hourly_wage_usd'].values[0])
                county_job_dict['annual_mean_wage_usd'].append(row['annual_mean_wage_usd'].values[0])
                county_job_dict['mean_wage_rse_percent'].append(row['mean_wage_rse_percent'].values[0])
                county_job_dict['msa_code'].append(row['county_code'].values[0])
                county_job_dict['county_name'].append(county_name)
                county_job_dict['msa_job'].append(':'.join([county_name, occupation_title])) # use this to remove data from the graph!
                
                new_remove_button = html.Button(
                    children='remove '+str(len(children)),
                    id= {
                        'type': 'remove-single-graph',
                        'index': len(children)
                    }
                )
                children.append(new_remove_button)
            else:
                print('you\'ve already entered that pair before!')
        else:
            # print(county_name, occupation_title)
            print('row was empty. no results found!!! >:(')
        
        # print(wage_data_to_graph)
    elif n_clicks > 0:# think of a better condition to check for remove!!!
        index_to_remove = ctx.triggered_id['index']
        county_to_remove = None
        occupation_to_remove = None
        print(f'index to remove: {index_to_remove}')
        for col in county_job_dict:
            if col == 'county_name':
                county_to_remove = county_job_dict['county_name'][index_to_remove]
                print(f'to remove: {county_to_remove}')
            elif col == 'occupation_title':
                occupation_to_remove = county_job_dict['occupation_title'][index_to_remove]
                print(f'to remove: {occupation_to_remove}')
            del county_job_dict[col][index_to_remove]
        children.pop()

        # print('==============')

        # remove from the msa_job_set set as well!
        # print(type(msa_job_set))
        # print(msa_job_set)
        # print(county_to_remove)
        # print(occupation_to_remove)
        print(f'entered_county_job_pairs: {entered_county_job_pairs}')
        print(f'use this to remove: {(county_to_remove, occupation_to_remove)}')
        entered_county_job_pairs.remove([county_to_remove, occupation_to_remove])
        # print(msa_job_set)

    wage_data_to_graph_df = pd.DataFrame(data=county_job_dict)
    # print(ctx.triggered_id)
    # print(type(ctx.triggered_id))
    # TODO: next steps!!!!
    # 1. adding in a remove button for graph data
    # 2. get data for all jobs within a particular state. So have state as a drop down and show all data for that state!
    # 3. adding in the other data points in differnt graphs below!
    # 4. deploy onto a cloud platform so other people can use/check it out!
    return (children,
    px.bar(wage_data_to_graph_df, y='annual_mean_wage_usd', hover_data=['county_name', 'occupation_title']),
    px.bar(wage_data_to_graph_df, y='median_hourly_wage_usd', hover_data=['county_name', 'occupation_title']),
    county_job_dict,
    entered_county_job_pairs
    )

# next steps:
# need to use the county that was entered and the occupation to retrieve the appropriate data from the wage dataframe

# from there, need to somehow take that data and graph it out
    # at this point probably stick to graphing each column of the row in separate graphs
    # ie. wage, employment data, etc... will each have their own graph

# for now, using the user entered data, try just to print out the corresponding row in the wage dataframe. That'll be pretty cool already!

# actually, for now,just try to print out the values the user gave first on clicking the button!

# check out the section in basic callbacks where 


if __name__ == '__main__':
    app.run_server(debug=True)
