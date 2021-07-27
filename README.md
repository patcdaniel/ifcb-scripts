# IFCB MBARI Scripts

Collections of loose scripts and notebooks for IFCB debugging and processing.

| Notebook                       | Description |
|--------------------------------|-------------|
| SCW-1-auto_class_display.ipynb |Access auto_classifier data from the SC Wharf IFCB|
| SCW-2-recent-plot.ipynb        |Access the most recent data from the SC wharf IFCB using the API |
| SCW-3-generate-TS.ipynb        |Generate a time series from the past 30 days of data from the SC wharf|
| ifcb-raw-peakROI-plots.ipynb   |Generate peak-roi-y plots from raw IFCB data |
| ifcb-raw-view-images.ipynb     |View raw images from the raw IFCB data |
| ifcb-raw-plot-max-image-size.ipynb   |Plot maximum image size from raw IFCB data |

## Jupyter Notebooks

Jupyter notebooks are stored under the `/notebooks` directory. They can be run directly on the remote machines with a portforwarding to interact in browser.

To run on particle (this requires installing a local version of anaconda):

```
jupyter notebook --ip=0.0.0.0 --port=8080 --no-browser
```

Then on your machine, you can run:

```
ssh -L 8080:localhost:8080 username@particle.shore.mbari.org
```

Finally open a browser and enter the url `localhost:8080/`.
