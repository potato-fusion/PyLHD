# PyLHD
[ ![Codeship Status for fujii-team/PyLHD](https://app.codeship.com/projects/60a2f6f0-e2fd-0134-1b72-664f30205a5b/status?branch=master)](https://app.codeship.com/projects/205940)
[![codecov](https://codecov.io/gh/fujii-team/PyLHD/branch/master/graph/badge.svg?token=KPHjGOJeMr)](https://codecov.io/gh/fujii-team/PyLHD)


Python library for the LHD experiments.

This library includes several components.

Currently, we mainly support input/output scripts that can handle LHD experiment data.

## Input/Output
+ eg: Module that read and write eg data format that is used as *analyzed-data*.  
This module is built on top of [**xarray**](http://xarray.pydata.org/),
which brings N-dimensional variants of the core pandas data structures.  
The basic usage can be found in this [**notebook**](notebooks/eg.ipynb).

+ igetfile: Module that download the analyzed data files from *analyzed data server*.  
This module generates eg data file,
so that the above *eg* module can be used for the downloaded file.  
The basic usage can be found in this [**notebook**](notebooks/igetfile.ipynb).
Note that this only works in the NIFS-experiment-network.

+ retrieve: Download raw data files from raw data server.  
Note that this only works in the NIFS-experiment-network.



+ PVwave: Read PVwave binary file from Python.

To use the above files, please contact us.
