from dash import Dash, dcc, html, Input, Output, State
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


app.layout = html.Div([
    'County',
    dcc.Dropdown(counties, placeholder='type in a county!', id='county-names'),
    'Job',
    dcc.Dropdown(occupation_titles, placeholder='type in a job!', id='occupation-titles'),
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    html.Div(id='output-state')
])

# this callback is ripped from here: https://dash.plotly.com/basic-callbacks. Check the submit button section to finish this off
# for the case of giving montreal, canada as the input
@app.callback(Output('output-state', 'children'),
              Input('submit-button-state', 'n_clicks'),
              State('county-names', 'value'),
              State('occupation-titles', 'value'))
def update_output(n_clicks, input1, input2):
    return u'''
        The Button has been pressed {} times,
        Input 1 is "{}",
        and Input 2 is "{}"
    '''.format(n_clicks, input1, input2)

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
