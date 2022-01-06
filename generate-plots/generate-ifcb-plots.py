import requests, json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import glob
import datetime as dt
import requests
from tqdm import tqdm
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def load_dataframe():
    last_file = sorted(glob.glob("/u/pdaniel/ifcb-scripts/data/classified-csv/classified_*.csv"))[-1]
    df = pd.read_csv(last_file)
    df.index = pd.to_datetime(df['dateTime'])

    critter_cols = [col for col in df.columns if col not in ['volume_analyzed','dateTime','nsample', 'inhibitTime', 'runTime', 'syringeSize','fileName','volume_analyzed','nsamples']]
    not_species = ['dateTime',"inhibitTime","runTime","nsample","volume_analyzed","syringeSize",'fileName','nsamples','nsample','ntotals','volume_analyzed','hab','date']
    habs = ["Pseudo-nitzschia","Alexandrium_singlet","Dinophysis","Lingulodinium","Cochlodinium","Prorocentrum","Gymnodinium","Karenia","Protoperidinium"]
    species = [cols for cols in df.columns if cols not in not_species]
    not_habs = [cols for cols in df.columns if (cols not in not_species) & (cols not in habs)]
        
    flowrate = 0.25; # .25 mls per minute
    df['volume_analyzed'] = ((df['runTime'] - df['inhibitTime']) * flowrate)/60
    df['nsamples'] = df[critter_cols].sum(axis=1)
    df[critter_cols] = df[critter_cols].divide(df['volume_analyzed'],axis=0)
    
    # Get top columns for the past week
    now = dt.datetime.now()
    week_ago = now - dt.timedelta(days=7)
    top_cols = df.query("index > @week_ago").iloc[-1][critter_cols].sort_values(ascending=False)[:15]
    top_cols = list(top_cols.index)

    return df, top_cols

def this_week(ax, n_days=10):
        """set x-lim of an axes to the past week"""
        now = dt.datetime.now()
        week_ago = now - dt.timedelta(days=n_days)
        ax.set_xlim(week_ago, now)

print("testing!!!")

if __name__ == "__main__":
    print("testing!!!")
    # df, top_classes = load_dataframe()
    # print(df.head())
    # print("testing")