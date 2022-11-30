import psycopg2
import pandas as pd

import datetime as dt
import matplotlib.dates as mdates
from matplotlib.collections import PolyCollection

def db_rack4():
    QUERY_ct="""SELECT DISTINCT a.slide_name as slide, a.instrument_name as instrument, q.name, q.star_time as duration_start, q.end_time as duration_end, aq.start_time as cycle_start, aq.end_time as cycle_end
    FROM dbo.anl a
    JOIN dbo.acq q on q.slide_id = a.slide_id and a.instrument_name = q.instrument and a.acquisition_name = q.name
    JOIN dbo.acq_scan aq on q.id = aq.acquisition_id
    ORDER BY a.slide_name"""

    #connect to the db (Rack4)
    conn = psycopg2.connect(database="analysis", host="192.168.7.190",user="analysisuser", password="Ether237", port="54320")

    #create a cursor to perform db
    cur = conn.cursor()
    #print(conn.get_dsn_parameters(), "\n")

    #execute a SQL query
    cur.execute(QUERY_ct)
    #Fetch result
    rows = cur.fetchone()
    #print("connected to - ", rows, "\n")

    df = pd.read_sql(QUERY_ct, conn)
    cur.close()
    conn.close()
    #print("connection is closed")

    df1 = df.copy()
    df1['duration_start'] = pd.to_datetime(df1['duration_start'], format='%Y-%m-%d %H:%M:%S')
    df1['duration_end'] = pd.to_datetime(df1['duration_end'], format='%Y-%m-%d %H:%M:%S')
    df1['cycle_start'] = pd.to_datetime(df1['cycle_start'], format='%Y-%m-%d %H:%M:%S')
    df1['cycle_end'] = pd.to_datetime(df1['cycle_end'], format='%Y-%m-%d %H:%M:%S')

    df1['duration'] = df1['duration_end']-df1['duration_start']
    df1['duration_day'] = df1['duration'].dt.total_seconds().div(3600).div(24)
    df1['scan_time'] = df1['cycle_end']-df1['cycle_start']
    df1['scan_sec'] = df1['scan_time'].dt.total_seconds()
    df1['scan_min'] = df1['scan_sec'].div(60)

    df1.index = df1['duration_start']
    return df1