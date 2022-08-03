import glob, os
import numpy as np

base_name = "/opt/ifcb-data/power-buoy-deployment/CA-IFCB-161/2022/"
dirs = os.listdir(base_name)

def unique(list1):
    # insert the list to the set
    list_set = set(list1)
    # convert the set to the list
    unique_list = (list(list_set))
    return unique_list


for directory in dirs:
    fnames = (glob.glob(os.path.join(base_name,directory + "/*")))
    fnames = [os.path.basename(f)[:-4] for f in fnames]
    values, counts = np.unique(fnames, return_counts=True)
    for v,c in zip(values,counts):
        if c != 3:
            ssh_command = "scp -l 1000 ifcb@buoy-ifcb.shore.mbari.org:/mnt/data/ifcbdata/{}.* /opt/ifcb-data/power-buoy-deployment/".format(v)
            print(v,c,ssh_command)

