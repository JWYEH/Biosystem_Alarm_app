import pandas as pd
from datetime import timedelta
from database import db_rack4
import os
baseOB2 = '/mnt/Y/'
baseOB3 = '/mnt/OB3/'

def get_slideOB2():
    df1 = db_rack4()
    slide = [j for j in df1[df1['instrument'] == 'OneBox-02']['slide']][::-1]
    return slide

def get_slide():
    df1 = db_rack4()
    slide = [j for j in df1['slide']][::-1]
    return slide

def get_instrument(slide):
    df1 = db_rack4()
    instrument = df1[df1['slide'] == slide].iloc[0]['instrument']
    return instrument

def get_duration(slide):
    listD = []
    df1 = db_rack4()
    duration_start = df1[(df1['slide'] == slide)] .iloc[0]['duration_start']
    duration_end = df1[(df1['slide'] == slide)].iloc[0]['duration_end']
    duration_start_dat = df1[(df1['slide'] == slide)] .iloc[0]['duration_start'].date()
    duration_end_dat = df1[(df1['slide'] == slide)].iloc[0]['duration_end'].date()
    cycle_N = len(df1[(df1['slide'] == slide)])
    per = pd.date_range(start=duration_start, end=duration_end, freq='D')
    for i in per: #create list of period of date
        listD.append(i.strftime('%Y-%m-%d'))
    return duration_start_dat, duration_end_dat, listD, cycle_N, duration_start, duration_end


def org_df(df):
    df['sep'] = [f[0:2] for f in df['DATE_TIME']]
    index = df[(df['sep'] != '20')].index
    df.drop(index, inplace=True)
    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'], format='%Y-%m-%d %H:%M:%S')
    df['M00'] = [f.split(']')[-1][3:] for f in df['M0']]
    df0 = df.drop(['sep'], axis=1)
    return df0

# end/duration df
def end_df(df):
    end = df[df['M00'].str[:4] == 'WFe-'].copy()
    end['MESSAGE'] = end['M00']+end['M1'].astype(str)+end['M2'].astype(str)+end['M3'].astype(str)+\
                     end['M4'].astype(str)+end['M5'].astype(str)+end['M6'].astype(str)+\
                     end['M7'].astype(str)+end['M8'].astype(str)+end['M9'].astype(str)+ \
                     end['M10'].astype(str) + end['M11'].astype(str) + end['M12'].astype(str) + end['M13'].astype(str) +\
                     end['M14'].astype(str)
    end = end.drop(['M0', 'M00', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12', 'M13', 'M14'
                    ], axis=1)
    end['main'] = [f.split('/')[0][4:] for f in end['MESSAGE']]
    end['sub'] = [f.split('--')[1].split('(')[0] for f in end['MESSAGE']]
    end['sub2'] = [f.split('--')[2].split('/')[0] for f in end['MESSAGE']]
    end['steps'] = [f.split('--')[0].split('/')[1:] for f in end['MESSAGE']]
    end['step_len'] = end['steps'].apply(len)
    end['elapsed_time'] = [int(f.split('elapsedMs:')[-1].split('nan')[0]) for f in end['MESSAGE']]
    end['time_s'] = end['elapsed_time']/1000
    end['time_m'] = end['time_s']/60
    end['time_h'] = end['time_m']/60
    end['steps'] = end['steps'].apply(tuple)
    end.index = end['DATE_TIME']
    return end


def loadtable(slide):
    listd = get_duration(slide)[2]

    def logfiles(listd, path):
        m = []
        for i in os.listdir(path):
            j = i[:10]
            for k in listd:
                if k in j:
                    m.append(i)
        return m

    Instrument = get_instrument(slide)
    if Instrument == 'OneBox-02':
        logpath = baseOB2
    elif Instrument == 'OneBox-03':
        logpath = baseOB3

    files = logfiles(listd, logpath)
    print (files)
    #files = logfiles(listd, baseOB2)

    # Read all log files + concat
    endAll = pd.DataFrame(
        columns=['DATE_TIME', 'MESSAGE', 'main', 'sub', 'steps', 'step_len', 'elapsed_time', 'time_s', 'time_m',
                 'time_h'])
    for file in files:
        logdf = pd.read_csv(logpath + file,
                            names=['DATE_TIME', 'M0', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9',
                                   'M10',
                                   'M11', 'M12', 'M13', 'M14'],
                            low_memory=False)
        # organize df:
        logdf0 = org_df(logdf)
        end = end_df(logdf0)
        # concat all end-logs
        endAll = pd.concat([endAll, end])
    return endAll

# create several list for matplotlib plot
def bar(dfe):
    ls1, ls2, ls3, ls4, ls5, ls6, ls7 = [], [], [], [], [], [], []
    for i in range(len(dfe)):
        list1 = dfe['DATE_TIME'][i] # finish time
        list2 = -dfe['time_h'][i]/24 #1. elaspse time(d)
        list3 = dfe['sub'][i] #2. sub
        list4 = dfe['DATE_TIME'][i] - timedelta(hours=dfe['time_h'][i]/2) # 3. middle time
        list5 = -dfe['time_h'][i] #5. elaspse time(h)
        list6 = dfe['sub2'][i] #6. sub
        list7 = -dfe['time_m'][i] #7. elaspse time(m)
        ls1.append(list1)
        ls2.append(list2)
        ls3.append(list3)
        ls4.append(list4)
        ls5.append(list5)
        ls6.append(list6)
        ls7.append(list7)
        list_tuple = list(zip(ls1, ls2)) #0
    return list_tuple, ls5, ls3, ls4, ls7, ls6

