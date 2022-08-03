from matplotlib.pyplot import cla
import tensorflow as tf
import keras_preprocessing.image as keras_img
import numpy as np
import glob
import tensorflow_addons as tfa
import pandas as pd
import json
import ifcb
from PIL import Image
from tqdm import tqdm
import os
import datetime as dt
import warnings
warnings.filterwarnings('ignore')


class ClassifyDashboard:
    def __init__(self):
        self.baseDir =  "/u/pdaniel/ifcb-scripts/"
        self.model = self.load_model()
        self.classes = self.load_class_labels()
        self.roi_fnames = self.generate_image_list()


    def load_model(self):
        """ Load Model off of google drive """
        model_dir = "/u/pdaniel/ifcb-scripts/classifier/ifcb-xception/"
        return tf.keras.models.load_model(model_dir)

    
    def load_class_labels(self):
        """ Load dict of class lables """
        label_dir = "/u/pdaniel/ifcb-scripts/classifier/xception-class-label.json"
        with open(label_dir) as json_file:
            return json.load(json_file)
    
    
    def generate_image_list(self):
        """Generate a list of ROI files to read image data from"""
        fnames = sorted(glob.glob("/opt/ifcb-data/power-buoy-deployment/CA-IFCB-161/2022/*/*.roi"))
        # This is a hotfix to get data after the 20th. need to implement something more robust
#         fnames = [f for f in fnames if int(os.path.basename(f)[7:9])>=20]
        return fnames

    
    def prep_image(self, image):
        """Load and prep images for model, reshape and normalize rgb to greyscale"""
        target_size=(224,224)
        img = keras_img.img_to_array(Image.fromarray(image).resize(target_size))
        img /= 255
        img = img.reshape((1, img.shape[0], img.shape[1], img.shape[2]))
        return img

    
    def build_image_stack(self, fname):
        """ Given a URL, get the zip file and unzip the images into a images stack for the model to read """
        try:
            with ifcb.open_raw(fname) as roi_data:
                array_index = 0
                roi_names = []
                img_stack = np.empty(shape=(len(roi_data.images),224,224,3))
                
                for roi_num, img_data in roi_data.images.items():
                    img_stack[array_index,:,:,:] = self.prep_image(img_data)
                    array_index += 1
                    roi_names.append(roi_num)
                    
        except Exception as e:
             print(fname, e)
                
        return img_stack, roi_names

    
    def get_label(self, sample_value, labels):
        """ Helper function to get the label from the class index"""
        for label, value in labels.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
            if value == sample_value:
                return(label)

    def run_model(self, image_stack, i):
        """Classify the image stack"""
        try:
            yhat = self.model.predict(image_stack[0])
        except:
            print(image_stack[0])
        self.processing_results(yhat,i)

    def processing_results(self, yhat, i, thresh=.75):
        """ Covert classifications into counts for each timestep """
        headers = list(self.classes.keys())
        thresh_array = np.repeat(thresh, yhat.shape[0])
        max_confidence = yhat.max(axis=1)
        unclass = np.where(max_confidence < thresh_array)
        max_ix = yhat.argmax(axis=1)
        max_ix[unclass] = 50
        totals = np.bincount(max_ix, minlength=51)

        self.classData[i,:] = totals
        
    def str_to_dt(self, datetime_str):
            return pd.to_datetime(datetime_str[1:])
    
    def add_datetime(self, fnames):
        """ Get sample times from based on the file names """
        self.output['dateTime'] = [self.str_to_dt(os.path.basename(f).split("_")[0]) for f in fnames]

    def add_metadata(self, fnames):
        """Add header data from syringe sample"""
        self.output[["inhibitTime","runTime","syringeSize",'fileName']] = ""
        inhibitTime = []
        runTime = []
        syringeSize = []
        fileName = []
        for fname in fnames:
            with ifcb.open_raw(fname) as roi_data:
                header = roi_data.headers
                inhibitTime.append(header["inhibitTime"])
                runTime.append(header["runTime"])
                syringeSize.append(header["syringeSize"])
                fileName.append(os.path.basename(fname))

        self.output['runTime'] = runTime
        self.output['inhibitTime'] = inhibitTime
        self.output['syringeSize'] = syringeSize
        self.output['fileName'] = fileName
            
    def save_data(self,fname=None):
        """Save pandas dataframe """
        if fname is None:
            #Create a filename based on datarange
            pass
        else:
            out_name = fname
        self.output.to_csv(os.path.join(self.baseDir,"data/classified-csv/",fname),index=False)


    def run(self, last_file=None, save_output=False):
        """ Main loop for running the   model on all of the data """
        if last_file is not None:
            if last_file == "latest":
                last_file = sorted(glob.glob("/u/pdaniel/ifcb-scripts/data/classified-csv/classified_*"))[-1]
            old_data = pd.read_csv(last_file)
            # Find last file to be processed based on df
            last_file = old_data.iloc[-1]['fileName']
            newest_file_ix = [i+1 for i, f in enumerate(self.roi_fnames) if os.path.basename(f) == last_file][0]
            # Make a new list of files
            self.roi_fnames = self.roi_fnames[newest_file_ix:]

        self.classData = np.empty((len(self.roi_fnames),len(self.classes))) # preallocate the totals for each sample
        

        for i, fname in tqdm(enumerate(self.roi_fnames), total=len(self.roi_fnames)):
            img_stack = self.build_image_stack(fname)
            self.run_model(img_stack,i)

        self.output = pd.DataFrame(data=self.classData, columns=self.classes)
        self.add_datetime(self.roi_fnames)
        self.add_metadata(self.roi_fnames)
        if last_file is not None:
            self.output = pd.concat((old_data, self.output))
            
        if save_output:
            out_filename = "classified_" + self.output.iloc[-1].fileName.split(".")[0] + ".csv"
            self.save_data(out_filename)

    
