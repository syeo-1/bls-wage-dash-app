from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import sqlite3

import json

# check the "simple example" section here for reference: https://dash.plotly.com/clientside-callbacks

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

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
    'County',
    dcc.Dropdown(counties, placeholder='type in a county!', id='county-names'),
    'Job',
    dcc.Dropdown(occupation_titles, placeholder='type in a job!', id='occupation-titles'),
    html.Button(id='submit-button-state', n_clicks=0, children='Display Data'),
    html.Div(id='remove-graphs', children=[]),
    html.Div(id='output-state'),
    dcc.Graph(id='annual_mean_wage_usd')
])

wage_data_to_graph = {
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
}
msa_job_set = set()
# print(wage_df.columns)

# pressing a remove will rerender based on the button list, not based on the
# data shown in the graphs!

# check pattern-matching callbacks section!
# the section for multiple filters could help!
# this should create the buttons for removal, but won't give functionality!
@app.callback(Output('remove-graphs', 'children'),
              Input('submit-button-state', 'n_clicks'),
              State('remove-graphs', 'children'))
def update_removal_list(n_clicks, children):
    # new_remove_button = html.Button(id=':'.join([occupation_title, county_name]))
    if n_clicks == 0: return children
    new_remove_button = html.Button(children='remove '+str(len(children)), id=str(n_clicks))
    children.append(new_remove_button)
    return children

# this callback is ripped from here: https://dash.plotly.com/basic-callbacks. Check the submit button section to finish this off
# for the case of giving montreal, canada as the input
@app.callback(Output('annual_mean_wage_usd', 'figure'),
              Input('submit-button-state', 'n_clicks'),
              State('county-names', 'value'),
              State('occupation-titles', 'value'))
def update_output(n_clicks, county_name, occupation_title):

    # get the county_code with the county name user has given

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
        if not (county_name, occupation_title) in msa_job_set:
            msa_job_set.add((county_name, occupation_title))
            print('===')
            print(row['employment'].values[0])
            print(row)
            print('===')
            wage_data_to_graph['occupation_title'].append(occupation_title)
            wage_data_to_graph['employment'].append(row['employment'].values[0])
            wage_data_to_graph['employment_rse_percent'].append(row['employment_rse_percent'].values[0])
            wage_data_to_graph['employment_per_1000_jobs'].append(row['employment_per_1000_jobs'].values[0])
            wage_data_to_graph['location_quotient'].append(row['location_quotient'].values[0])
            wage_data_to_graph['median_hourly_wage_usd'].append(row['median_hourly_wage_usd'].values[0])
            wage_data_to_graph['mean_hourly_wage_usd'].append(row['mean_hourly_wage_usd'].values[0])
            wage_data_to_graph['annual_mean_wage_usd'].append(row['annual_mean_wage_usd'].values[0])
            wage_data_to_graph['mean_wage_rse_percent'].append(row['mean_wage_rse_percent'].values[0])
            wage_data_to_graph['msa_code'].append(row['county_code'].values[0])
            wage_data_to_graph['county_name'].append(county_name)
            wage_data_to_graph['msa_job'].append(':'.join([county_name, occupation_title])) # use this to remove data from the graph!
        else:
            print('you\'ve already entered that pair before!')
    else:
        print(county_name, occupation_title)
        print('row was empty. no results found!!! >:(')
    
    print(wage_data_to_graph)
    wage_data_to_graph_df = pd.DataFrame(data=wage_data_to_graph)

    # TODO: next steps!!!!
    # 1. adding in a remove button for graph data
    # 2. get data for all jobs within a particular state. So have state as a drop down and show all data for that state!
    # 3. adding in the other data points in differnt graphs below!
    # 4. deploy onto a cloud platform so other people can use/check it out!
    return px.bar(wage_data_to_graph_df, y='annual_mean_wage_usd', hover_data=['county_name', 'occupation_title'])

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
