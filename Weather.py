import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class HTMLTableParser:
    def parse_html_table(self, table):
        n_columns = 0
        n_rows = 0
        column_names = []

        # Find number of rows and columns
        # we also find the column titles if we can
        for row in table.find_all('tr'):

            # Determine the number of rows in the table
            td_tags = row.find_all('td')
            if len(td_tags) > 0:
                n_rows += 1
                if n_columns == 0:
                    # Set the number of columns for our table
                    n_columns = len(td_tags)

            # Handle column names if we find them
            th_tags = row.find_all('th')
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.get_text())

        # Safeguard on Column Titles
        if len(column_names) > 0 and len(column_names) != n_columns:
            raise Exception("Column titles do not match the number of columns")

        columns = column_names if len(column_names) > 0 else range(0, n_columns)
        df = pd.DataFrame(columns=columns,
                          index=range(0, n_rows))
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            for column in columns:
                df.iat[row_marker, column_marker] = column.get_text()
                column_marker += 1
            if len(columns) > 0:
                row_marker += 1

        # Convert to float if possible
        for col in df:
            try:
                df[col] = df[col].astype(float)
            except ValueError:
                pass

        return df
def give_results(date,city,state,code):     # date = 2017/2/10

    if bool(re.search('[a-zA-Z]',code)):
        url_to_scrape = 'https://www.wunderground.com/history/airport/' + code + '/' + str(date) + '/DailyHistory.html?req_city=' + city + '&req_statename=' + state + '&MR=1'
    else:
        url_to_scrape = 'https://www.wunderground.com/history/wmo/' + code + '/' + str(date) + '/DailyHistory.html?req_city=' + city + '&req_statename=' + state + '&MR=1'

    r = requests.get(url_to_scrape)
    soup = BeautifulSoup(r.text,"lxml")
    required_table = soup.find_all('table')[4]  # Grab the last table
    hp = HTMLTableParser()
    table = hp.parse_html_table(required_table) # Grabbing the table from the tuple

    table['Temp.'] = table['Temp.'].map(lambda x: x.lstrip('\n').rstrip(' °C\n'))
    table['Dew Point'] = table['Dew Point'].map(lambda x: x.lstrip('\n').rstrip(' °C\n'))
    table['Humidity'] = table['Humidity'].map(lambda x: x.lstrip('').rstrip('%'))
    table['Pressure'] = table['Pressure'].map(lambda x: x.lstrip('\n').rstrip(' hPa\n'))
    table['Wind Speed'] = table['Wind Speed'].map(lambda x: str(x)[1:4])

    table.rename(columns={'Temp.':'Temp. (°C)','Humidity':'Humidity (%)' , 'Dew Point':'Dew Point (°C)' ,'Pressure':'Pressure (hPa)' ,'Wind Speed':'Wind Speed (km/h)'}, inplace=True)

    del table["Events"]
    del table["Precip"]
    del table["Gust Speed"]
    del table["Visibility"]
    del table["Wind Dir"]

    return table

weather_details = give_results("2017/1/1","Pallekele","Sri Lanka","43444")
print(weather_details)