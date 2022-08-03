import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
import tensorflow as tf
import keras_preprocessing.image as keras_img
import numpy as np
import glob, time, csv, multiprocessing, pickle
from PIL import Image
import ifcb
import cProfile

tf.get_logger().setLevel('INFO')

open_file = open("./classifier/scwharf-25-class/class-names.pkl", "rb")
LABELS = pickle.load(open_file)
open_file.close()

model_dir = "./classifier/scwharf-25-class/models"
MODEL = tf.keras.models.load_model(model_dir)


def prep_image(image):
    """Load and prep images for model, reshape and normalize rgb to greyscale"""
    target_size=(224,224)
    img = keras_img.img_to_array(Image.fromarray(image).resize(target_size))
    img /= 255
    img = img.reshape((1, img.shape[0], img.shape[1], img.shape[2]))
    return img

def build_image_stack(fname):
    """ Given a URL, get the zip file and unzip the images into a images stack for the model to read """
    with ifcb.open_raw(fname) as roi_data:
        array_index = 0
        roi_names = []
        img_stack = np.empty(shape=(len(roi_data.images),224,224,3))
        for roi_num, img_data in roi_data.images.items():
            img_stack[array_index,:,:,:] = prep_image(img_data)
            array_index += 1
            roi_names.append(roi_num)

    return img_stack, roi_names


def get_results(fname):
    data_array, roi_names = build_image_stack(fname)
    results = MODEL.predict(data_array)
    ixs = results.argmax(axis=1)
    best_guess = [LABELS[ix] for ix in ixs]
    perc = results.max(axis=1)
    return best_guess, perc, roi_names

def classify_roi(fname):
    out_name  = os.path.basename(fname).split("_")[0] + ".csv"
    print("Opening {}".format(out_name.split(".")[0]))
    label, conf, roi_names = get_results(fname)
    write_out(out_name,label,conf,roi_names)

def write_out(fname,label,conf,roi_names):
    with open(os.path.join("./data/multiprocess-output/",fname), 'w') as f:
        writer = csv.writer(f)
        writer.writerows(zip(label, conf, roi_names))

        
def multi_classification(processes,fnames):
    """ Run multiprocessing prime finder """
    with multiprocessing.Pool(processes) as pool:
        output = pool.map(classify_roi,fnames)
        pool.close()


if __name__ == "__main__":
    fnames = sorted(glob.glob("/opt/ifcb-data/power-buoy-deployment/CA-IFCB-161/2022/D20220419/*.roi"))
    start = time.perf_counter()
    for fname in fnames:
        classify_roi(fname=fname)
    finish = time.perf_counter()
    print(f'{len(fnames)} files in {round(finish-start,2 )} second(s)')