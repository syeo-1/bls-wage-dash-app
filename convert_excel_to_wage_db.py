import sqlite3
import pandas as pd

# connect to the database
conn = sqlite3.connect('wage_stats.db')

# open the excel county data file using pandas
county_data = pd.read_excel('area_definitions_m2021.xlsx', index_col=0)

# insert the data into the sqlite wages database
county_data.to_sql('region_data', con=conn)

# call the table region data

print(county_data)
conn.close()
