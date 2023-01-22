from dash import Dash, dcc, html, Input, Output, State, ctx, ALL
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
    dcc.Graph(id='hourly_median_wage_usd'),
    dcc.Graph(id='annual_mean_wage_usd'),
    
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
# @pp.callback(
#     Output('remove-graphs', 'children'),
#     Output('annual_mean_wage_usd', 'figure'),
#               Input('submit-button-state', 'n_clicks'),
#               Input({'type': 'remove-single-graph', 'index': ALL}, 'n_clicks'),
#               State('remove-graphs', 'children'))
# def update_removal_list(n_clicks, _, children):
#     # new_remove_button = html.Button(id=':'.join([occupation_title, county_name]))

#     # TODO:
#     # bug: if the wage data already exists, the remove button will still be
#     # created. Need to somehow check here if the data already exists
#     # before creating a remove button for it
#     if n_clicks == 0: return children
#     if 'submit-button-state' == ctx.triggered_id:
#         new_remove_button = html.Button(
#             children='remove '+str(len(children)),
#             id= {
#                 'type': 'remove-single-graph',
#                 'index': len(children)
#             }
#         )
#         children.append(new_remove_button)
#         return children
#     else:
#         # a remove button was pressed. figure out which one 
#         # and remove it from the list of remove buttons!
#         # print(ctx.triggered_id)
#         index_to_remove = ctx.triggered_id['index']
#         for col in wage_data_to_graph:
#             del wage_data_to_graph[col][index_to_remove]
#         children.pop()
#         return childrena


# this callback is ripped from here: https://dash.plotly.com/basic-callbacks. Check the submit button section to finish this off
# for the case of giving montreal, canada as the input
@app.callback(
    Output('remove-graphs', 'children'),
    Output('annual_mean_wage_usd', 'figure'),
    Output('hourly_median_wage_usd', 'figure'),
              Input('submit-button-state', 'n_clicks'),
              Input({'type': 'remove-single-graph', 'index': ALL}, 'n_clicks'),
              State('remove-graphs', 'children'),
              State('county-names', 'value'),
              State('occupation-titles', 'value'))
def update_output(n_clicks, _, children, county_name, occupation_title):

    # get the county_code with the county name user has given

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
            if not (county_name, occupation_title) in msa_job_set:
                msa_job_set.add((county_name, occupation_title))
                # print('===')
                # print(row['employment'].values[0])
                # print(row)
                # print('===')
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
        for col in wage_data_to_graph:
            if col == 'county_name':
                county_to_remove = wage_data_to_graph['county_name'][index_to_remove]
                print(f'to remove: {county_to_remove}')
            elif col == 'occupation_title':
                occupation_to_remove = wage_data_to_graph['occupation_title'][index_to_remove]
                print(f'to remove: {occupation_to_remove}')
            del wage_data_to_graph[col][index_to_remove]
        children.pop()

        # print('==============')

        # remove from the msa_job_set set as well!
        # print(type(msa_job_set))
        # print(msa_job_set)
        # print(county_to_remove)
        # print(occupation_to_remove)
        msa_job_set.remove((county_to_remove, occupation_to_remove))
        print(msa_job_set)

    wage_data_to_graph_df = pd.DataFrame(data=wage_data_to_graph)
    # print(ctx.triggered_id)
    # print(type(ctx.triggered_id))
    # TODO: next steps!!!!
    # 1. adding in a remove button for graph data
    # 2. get data for all jobs within a particular state. So have state as a drop down and show all data for that state!
    # 3. adding in the other data points in differnt graphs below!
    # 4. deploy onto a cloud platform so other people can use/check it out!
    return (children,
    px.bar(wage_data_to_graph_df, y='annual_mean_wage_usd', hover_data=['county_name', 'occupation_title']),
    px.bar(wage_data_to_graph_df, y='median_hourly_wage_usd', hover_data=['county_name', 'occupation_title'])
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
