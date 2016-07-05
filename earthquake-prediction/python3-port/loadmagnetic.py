# NASA World Wind Earthquake load data code

from datetime import timedelta
from time import process_time
import pandas as pd
import bandfilter as bf
from urllib.parse import urlencode
import json 
import urllib.request
import stationsdata as st
from pandas.io.json import json_normalize

def load_magnetic_data(station, min_date, max_date, download = False):
    start = process_time()
    path = '../data/' + station + '/' + min_date + '-to-' + max_date + '.csv'
    
    if station[:3] == 'ESP': 
        if not download:
            print("Loading magnetic data", end='')
            df = load_magnetic_data_esp(path)

        else:
            print("Getting magnetic data", end='')
            df = get_magnetic_data_esp(station, min_date, max_date)

        # if filter_data:
        #     df = bf.filter(df)

        # else:     
        #     df = df.resample('1T').mean() 
        #     df = df.interpolate().dropna(how='any', axis=0)

        print(" --- took", round(process_time() - start, 2), " s")
        return df

    elif station[:10] == "InteleCell":
        if not download:
            print("Loading magnetic data", end='')
            df = load_magnetic_data_intele(path)

        else:
            Exception("Get InteleCell data not implemented")

        print(" --- took", round(process_time() - start, 2), " s")

        return df

    else:
        Exception("ERROR - No station recognized")

def load_magnetic_data_esp(path):
    column_names = ['Date', 'X', 'Y', 'Z']
    
    df = pd.read_csv(path, names=column_names)
    df.index = pd.to_datetime(df['Date'], utc=True)
    df.interpolate().dropna(how='any', axis=0)

    return df

def load_magnetic_data_intele(path):
    column_names = ['Date', 'X', 'Y', 'Z']
    
    df = pd.read_csv(path)
    df.drop('Unnamed: 4', axis=1, inplace=True)
    df.columns = column_names
    df.index = pd.to_datetime(df.Date, utc=True)
    df.dropna(how='any', axis=0)

    return df

def get_magnetic_data_esp(esp_station, min_date, max_date, intranet = False):

    station_map = { 'ESP-Kenny-Lake-1' : 10,
                    'ESP-Kodiak-2' : 11,
                    'ESP-Kodiak-3' : 7,
                    'ESP-Kodiak-4' : 8 }

    if intranet:
        resources_url = "http://10.193.20.17/download/"
    else:
        resources_url = "http://24.237.235.227/download/"

    dict_json = {
        "sensor": station_map[esp_station],
        "order": "asc",
        "format": "csv",
        "start_date": min_date,
        "end_date": max_date,
        "submit" : "Download+Data"
    }

    df = pd.read_csv(resources_url + "?" + urllib.parse.urlencode(dict_json), encoding='utf8',header=None)
    df.columns = ['Date', 'X', 'Y', 'Z']
    df.index = pd.to_datetime(df.Date, utc=True)

    return df

def upsample_to_min(magnetic):
    magnetic = magnetic.resample('1T').mean()
    magnetic = magnetic.interpolate().dropna(how='any', axis=0)
    magnetic['Date'] = magnetic.index

    return magnetic

def load_db(station, min_date, max_date, sample_size = 10):
    print("Loading magnetic data", end='')

    column_names = ['Date', 'X', 'Y', 'Z']
    start = process_time()
    resources_url = "http://143.232.136.208:8086/query"

    url = resources_url + "?" + "q=select+*+from+"
    url += st.get_esp_name(station)
    url += "+where+time+>+'" + min_date + "'"
    url += "+and+time+<+'" + max_date + "'"
    # url += "+limit+" + str(sample_size) 
    url += "&db=test_hmr"

    res = urllib.request.urlopen(url)
    str_data = res.read().decode('ascii')
    dict_data = json.loads(str_data)
    path = dict_data['results'][0]['series'][0]
    df_data = pd.DataFrame(path['values'], columns = column_names)
    df_data.index = pd.to_datetime(df_data['Date'], utc=True)
    df_data.dropna(how='any', axis=0)
       
    print(" --- took", round(process_time() - start, 2), " s")
    # print(df_data)
    return df_data

name, begin, end = 'ESP-Kodiak-3', '2016-06-03', '2016-06-04'

# print(load_db(name, begin, end))