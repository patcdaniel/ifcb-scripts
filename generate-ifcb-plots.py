import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import glob
import datetime as dt
import numpy as np
import seaborn as sns
import os
import ifcb
import itertools
import json


def load_dataframe():
    """ Load the classified IFCB Data """
    last_file = sorted(glob.glob("/u/pdaniel/ifcb-scripts/data/classified-csv/classified_*.csv"))[-1]
    df = pd.read_csv(last_file)
    df.index = pd.to_datetime(df['dateTime'])

    critter_cols = [col for col in df.columns if col not in ['volume_analyzed','dateTime','nsample', 'inhibitTime', 'runTime', 'syringeSize','fileName','volume_analyzed','nsamples']]
    not_species = ['dateTime',"inhibitTime","runTime","nsample","volume_analyzed","syringeSize",'fileName','nsamples','nsample','ntotals','volume_analyzed','hab','date']
    habs = ["Pseudo-nitzschia","Alexandrium_singlet","Dinophysis","Lingulodinium","Cochlodinium","Prorocentrum","Gymnodinium","Protoperidinium"]
    species = [cols for cols in df.columns if cols not in not_species]
    not_habs = [cols for cols in df.columns if (cols not in not_species) & (cols not in habs)]
    flowrate = 0.25; # .25 mls per minute
    df['volume_analyzed'] = ((df['runTime'] - df['inhibitTime']) * flowrate)/60
    df['nsamples'] = df[critter_cols].sum(axis=1)
    df[critter_cols] = df[critter_cols].divide(df['volume_analyzed'],axis=0)

    now = dt.datetime.now()
    week_ago = now - dt.timedelta(days=7)

    top_cols = df.query("index > @week_ago").iloc[-1][critter_cols].sort_values(ascending=False)[:15]
    top_cols = list(top_cols.index)

    return df, top_cols

def this_week(ax, n_days=10):
        """Help function to set x-lim of an axes to the past week"""
        now = dt.datetime.now()
        week_ago = now - dt.timedelta(days=n_days)
        ax.set_xlim(week_ago, now)

def timeseries_plots(df, classes, n_days=7, title="",full_records=False):
    """ Time series plots """
    ## Figure Formatting ##
    sns.set_context('talk')
    fig, (ax,ax2) = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    plt.subplots_adjust(hspace=.25)
    fig.set_size_inches(10,10)
    ax.set_title("IFCB 161 - Power Buoy {}".format(title), loc="left",pad=25,fontsize=20,fontweight='bold')
    ## Color formatting ##
    colors = sns.color_palette("hls", len(classes))
    ax.set_prop_cycle('color', colors)

    ## First Axis - IFCB Timeseries ##
    if not full_records:
        now = dt.datetime.now()
        week_ago = now - dt.timedelta(days=n_days)
        df = df.query("index > @week_ago")
    
    df[classes].plot(ax=ax)
    ax.legend(bbox_to_anchor=(1.01, 1.1), loc='upper left',frameon=False)
    ax.set_ylabel("Cells per mL")
    ## Tick and Date Formatting ##
    major_ticks = mdates.DayLocator(interval=1) # Major ticks every day.
    ax.xaxis.set_major_locator(major_ticks)
    ## Minor ticks every month. ##
    minor_ticks = mdates.HourLocator(byhour=range(2,24,2))
    ax.xaxis.set_minor_locator(minor_ticks)
    ## Text in the x axis will be displayed in 'YYYY-mm' format. ##
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    plt.xticks(rotation = 45) 
    ax.set_xlabel("")
    if not full_records:
        this_week(ax, n_days=n_days)
    top_yval = df[classes].max(axis=0).max()
    ax.set_ylim(0, top_yval+ 25)

    df['nsamples'].plot(ax=ax2)

    ax2.xaxis.set_major_locator(major_ticks)
    ax2.xaxis.set_minor_locator(minor_ticks)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))

    plt.xticks(rotation = 45) # Rotates X-Axis Ticks by 45-degrees
    ax.set_xlabel("")
    # ax.set_ylim(0, 151)
    # ax2.set_ylim(0, 2500)

    ax2.set_ylabel('ROI per mL')

    ax2.text(-.1,
            -.8,
            'pdaniel - generate-ifcb-plots.py - {}\nxception- https://bit.ly/ifcb-161-model'.format(str(dt.datetime.now())[:-7]),
            transform=ax.transAxes,
            fontsize='small',
            color='.5')
    if not full_records:
        this_week(ax2, n_days=n_days)
    ax2.set_xlabel("")

    sns.despine(ax=ax2)
    sns.despine(ax=ax)
    if not full_records:
        plt.savefig(os.path.join("/u/pdaniel/ifcb-scripts/figures",'161-classified-top-{}-day.png'.format(str(n_days))),dpi=300,bbox_inches='tight',transparent=False)
    else:
        plt.savefig(os.path.join("/u/pdaniel/ifcb-scripts/figures",'161-classified-top-all.png'.format(str(n_days))),dpi=300,bbox_inches='tight',transparent=False)


def habs_plots(df,n_days=7):
    """ Timeseries plots of only HAB species of interest """
    sns.set_context('talk')
    habs = ["Pseudo-nitzschia","Alexandrium_singlet","Dinophysis","Lingulodinium","Cochlodinium","Prorocentrum","Gymnodinium","Protoperidinium"]
    fig, ax = plt.subplots(constrained_layout=False)
    plt.subplots_adjust(hspace=.1)
    fig.set_size_inches(10,6)
    colors = sns.color_palette("hls", len(habs))
    ax.set_prop_cycle('color', colors)
    
    now = dt.datetime.now()
    week_ago = now - dt.timedelta(days=n_days)
    df = df.query("index > @week_ago")

    df[habs].plot(ax=ax)
    ax.legend(bbox_to_anchor=(1.01, 1.1), loc='upper left',frameon=False)
    ax.set_ylabel("Cells per mL")

    # Major ticks every 6 months.
    major_ticks = mdates.DayLocator(interval=1)
    ax.xaxis.set_major_locator(major_ticks)

    # Minor ticks every month.
    minor_ticks = mdates.HourLocator(12)
    ax.xaxis.set_minor_locator(minor_ticks)

    # Text in the x axis will be displayed in 'YYYY-mm' format.
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    plt.xticks(rotation = 45) # Rotates X-Axis Ticks by 45-degrees
    ax.set_xlabel("")
    this_week(ax, n_days=n_days)
    top_yval = df[habs].max(axis=0).max()
    if top_yval > 50:
        ax.set_ylim(0, top_yval+ 10)
    else:
        ax.set_ylim(0, 50+ 10)

    ax.text(-.1,
            -.35,
            'pdaniel - generate-ifcb-plots.py - {}'.format(str(dt.datetime.now())[:-7]),
            transform=ax.transAxes,
            fontsize='small',
            color='.5')

    plt.title("IFCB 161 - Power Buoy\nxception- https://bit.ly/ifcb-161-model")
    sns.despine()
    plt.savefig(os.path.join("/u/pdaniel/ifcb-scripts/figures",'161-classified-top-habs-{}-day.png'.format(str(n_days))),dpi=300,bbox_inches='tight',transparent=False)


def stacked_plots(df, classes, n_days=7, normalized=False):
    """ Stacked area plots of species of interest """
    fig, ax = plt.subplots()
    fig.set_size_inches(10,11)

    colors = sns.color_palette("hls", len(classes))
    ax.set_prop_cycle('color', colors)

    now = dt.datetime.now()
    week_ago = now - dt.timedelta(days=n_days)
    
    if normalized:
        critter_cols = [col for col in df.columns if col not in ['volume_analyzed','dateTime','nsample', 'inhibitTime', 'runTime', 'syringeSize','fileName','volume_analyzed','nsamples']]
        df['nsamples'] = df[critter_cols].sum(axis=1)
        df_norm = df[critter_cols].divide(df['nsamples'],axis=0)
        df_norm = df_norm.query("index > @week_ago")
        df_norm[classes].plot.area(ax=ax)
        ax.set_ylabel("Fraction of cells")

    else:
        df = df.query("index > @week_ago")
        df[classes].plot.area(ax=ax)
        ax.set_ylabel("Cells per mL")
    
    ax.legend(bbox_to_anchor=(1.01, 1.04), loc='upper left',frameon=False)
    

    this_week(ax, n_days=n_days)
    ax.text(-.1,
            -.2,
            'pdaniel - generate-ifcb-plots.py - {}'.format(str(dt.datetime.now())[:-7]),
            transform=ax.transAxes,
            fontsize='small',
            color='.5')

    plt.title("IFCB 161 - Power Buoy\nxception- https://bit.ly/ifcb-161-model")
    sns.despine()
    ax.set_xlabel("")
    if normalized:
        ax.set_ylim(0,1)
        plt.savefig(os.path.join("/u/pdaniel/ifcb-scripts/figures", '161-classified-stacked-norm-{}-day.png'.format(str(n_days))),dpi=300,bbox_inches='tight',transparent=False)
        ax.set_ylabel("Fraction of cells")
    else:
        plt.savefig(os.path.join("/u/pdaniel/ifcb-scripts/figures", '161-classified-stacked-top-{}-day.png'.format(str(n_days))),dpi=300,bbox_inches='tight',transparent=False)


def bead_plots():
    """ Make the ROI-Y/PMT[A,B] plots for acessing quality"""
    fnames = glob.glob("/opt/ifcb-data/power-buoy-deployment/beads/*.roi")
    fnames = fnames[-10:-1]
    for pmt in ["A","B"]:
        fig, ax = plt.subplots()
        fig.set_size_inches(8,8)
        sns.set_context('talk')
        palette = itertools.cycle(sns.color_palette(palette=sns.dark_palette("#69d", reverse=False)))
        for i, f in enumerate(fnames):
            data = load_peakROIY(f)
            if data is None:
                pass
            else:
                label = os.path.basename(f).split(".")[0].split("_")[0]
                if (i == (len(fnames)-1)):
                    sns.scatterplot(x="peak{}".format(pmt),y="ROIy",data=data,label=label, color='r')
                else:
                    sns.scatterplot(x="peak{}".format(pmt),y="ROIy",data=data,label=label, color=next(palette))

        ax.set_ylabel("ROI Y Pos")
        ax.set_xlabel("Volts")
        plt.legend(ncol=2,frameon=True,loc=(0,-.35))
        plt.title("PMT-{} MBARI 161 - Internal Beads".format(pmt))
        ax.text(0,
                -.4,
                'pdaniel - generate-ifcb-plots.py - {}'.format(str(dt.datetime.now())[:-7]),
                transform=ax.transAxes,
                fontsize='small',
                color='.5')
        plt.savefig(os.path.join("/u/pdaniel/ifcb-scripts/figures", 'ifcb-161-beads-PMT-{}.png'.format(pmt)),dpi=300,bbox_inches='tight',transparent=False, facecolor='white', pad_inches=0.1)
        plt.close()


def load_peakROIY(fname):
    """ Helper function for loading Bead data """
    adc_headers = ["trigger#",
                    "ADC_time",
                    "PMTA",
                    "PMTB",
                    "PMTC",
                    "PMTD",
                    "peakA",
                    "peakB",
                    "peakC",
                    "peakD",
                    "time_of_flight",
                    "grabtimestart",
                    "grabtimeend",
                    "ROIx",
                    "ROIy",
                    "ROIwidth",
                    "ROIheight",
                    "start_byte",
                    "comparator_out",
                    "STartPoint",
                    "SignalLength",
                    "status",
                    "runtime",
                    "inhibitTime"
                  ]
    try:
        data = ifcb.open_raw(fname)
        adc = data.images_adc
    except:
        return None
    
    for i, col in enumerate(adc.columns):
        adc.rename(columns={col:adc_headers[i]},inplace=True)
    adc.reset_index(inplace=True,drop=True)
    return adc


def makeMetadata_JSON():
    """ Make a metadata file to send along for website """
    run_time = dt.datetime.now()
    data = {'last_run':run_time. isoformat()}
    with open('/u/pdaniel/ifcb-scripts/data/process_ifcb.js', 'w', encoding='utf-8') as f:
        f.write("var ifcbData = [")
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("];\n")
        f.write('document.getElementById("last-updated").innerHTML= "Last Update on: " + ifcbData[0]["last_run"]')

def transfer_to_website():
    """
    Copy images from model runs to webserver where they can be viewed publically.
    Had to manually specifiy ssh key location with -i 
    """
    try:
        os.system('scp -i "/etc/ssh/keys/pdaniel/id_rsa" /u/pdaniel/ifcb-scripts/figures/*.png  skyrocket8.mbari.org:/var/www/html/data/ifcb-161/figures')
        os.system('scp -i "/etc/ssh/keys/pdaniel/id_rsa" /u/pdaniel/ifcb-scripts/data/process_ifcb.js  skyrocket8.mbari.org:/var/www/html/data/ifcb-161/figures')
    except:
        pass


def main():
    df, top_classes = load_dataframe()
    timeseries_plots(df,top_classes,n_days=3)
    timeseries_plots(df,top_classes,n_days=7)
    timeseries_plots(df,top_classes,full_records=True)
    habs_plots(df, n_days=3)
    habs_plots(df, n_days=7)
    stacked_plots(df, top_classes, n_days=3)
    stacked_plots(df, top_classes, n_days=7)
    stacked_plots(df, top_classes, n_days=3, normalized=True)
    stacked_plots(df, top_classes, n_days=7, normalized=True)
    bead_plots()
    makeMetadata_JSON()
    transfer_to_website()


if __name__ == "__main__":
    main()

