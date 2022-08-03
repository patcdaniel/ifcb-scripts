from ClassifyDashboard.mClassifier import ClassifyDashboard
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import glob, ifcb, os

def open_ifcb(file, fnames):
    """find ifcb file, open and get volume analyzed given a file name"""
    file = os.path.splitext(file)[0]
    ix = [i for i, fname in enumerate(fnames) if file in fname][0]
    ifcb_data = ifcb.open_raw(fnames[ix])
    return IFCB_volume_analyzed(ifcb_data)


def IFCB_volume_analyzed(ifcb):
    """ From ifcb-analysis"""
    looktime = ifcb.hdr_attributes['runTime'] - ifcb.hdr_attributes['inhibitTime'] # in Seconds
    flowrate = 0.25; # .25 mls per minute
    if looktime == 0:
        """A couple of .hdr files don't have run time values"""
        times = ifcb.adc[[22,23]].iloc[-1].values
        looktime = times[0] - times[1]
        print("{}:  looktime: {}".format(ifcb.lid,looktime))
        
        if looktime == 0:
            """Bug where last line of .adc is bad, look one earlier"""
            times = ifcb.adc[[22,23]].iloc[-2].values
            looktime = times[0] - times[1]
            print("AGAIN: {}:  looktime: {}".format(ifcb.lid,looktime))
            
    return flowrate*looktime/60

if __name__ == "__main__":
    ClassifyDashboard().run(last_file='latest', save_output=True)