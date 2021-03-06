'''
A function that reads eg file for the LHD experiment.
The typical usage is

>>> data = eg.load(filename)

The dimension axis is stored in self.dim (ordered dict), while the data are
stored self.val (ordered dict)

To check the contents,

>>> data.dim.keys()

>>> data.val.keys()

To access the data,

>>> data[key]

can be used.

Updated on Dec 12, 2016.
xarray support. Some methods are decided to be deprecated.
For the details, see http://xarray.pydata.org/

Updated on Oct 3, 2016
Created on Mar 28, 2016

@author: keisukefujii
'''

import numpy as np
from collections import OrderedDict
import warnings
from copy import deepcopy
from datetime import datetime
import pandas as pd
import xarray as xr

def load(filename):
    """
    Load eg-file and returns as xarray.DataSet.

    To load the data from a file,

    >>>  array = eg.load(filename)
    """
    """
    First, we load [Parameters] and [comments] parts of the eg-file.
    Parameters are stored in xarray.DataArray.attrs as an OrderedDict.
    """
    parameters = OrderedDict()
    comments = OrderedDict()
    # load [Parameters] and [Comments] section
    with open(filename, 'r') as f:
        for line in f:
            if '[parameters]' in line.lower():
                block = 'Parameters'
            elif '[comments]' in line.lower():
                block = 'comments'
            elif '[data]' in line.lower():
                break # data is read np.loadtxt
            elif not '#' in line:
                break # Finish reading.
            # read Parameters block
            elif block is 'Parameters':
                # Make lower case
                key = line[line.find('#')+1:line.find("=")].strip()
                # remove '(quotation) and , (space)
                val = line[line.find('=')+1:].replace(" ","").replace("'", "").strip()
                # string
                if key.lower() == 'NAME'.lower():
                    parameters['NAME'] = val
                # list of string
                elif key.lower() == 'DimName'.lower():
                    parameters['DimName'] = val.split(',')
                elif key.lower() == 'DimUnit'.lower():
                    parameters['DimUnit'] = val.split(',')
                elif key.lower() == 'ValName'.lower():
                    parameters['ValName'] = val.split(',')
                elif key.lower() == 'ValUnit'.lower():
                    parameters['ValUnit'] = val.split(',')
                # string
                elif key.lower() == 'Date'.lower():
                    parameters['Date'] = val
                # integers
                elif key.lower() == 'DimNo'.lower():
                    parameters['DimNo'] = int(val)
                elif key.lower() == 'ValNo'.lower():
                    parameters['ValNo'] = int(val)
                elif key.lower() == 'ShotNo'.lower():
                    parameters['ShotNo'] = int(val)
                elif key.lower() == 'SubShotNO'.lower():
                    parameters['SubShotNO'] = int(val)
                # list of integers
                elif key.lower() == 'DimSize'.lower():
                    parameters['DimSize'] = [int(s) for s in val.split(',')]
                else: # the rest of parameters                # string
                    if key is not None and len(key)>0:
                        parameters[key] = line[line.find('=')+1:].strip()

            elif block is 'comments':
                # Make lower case
                key = line[line.find('#')+1:line.find("=")].strip()
                # remove '(quotation) and , (space)
                val = line[line.find('=')+1:].replace(" ","").replace("'", "").strip()
                if key is not None and len(key)>0:
                    comments[key] = line[line.find('=')+1:].strip()

        # Make sure some necessary parameters are certainly stored
        need_keys = ['NAME', 'DimName', 'DimUnit', 'ValName', 'ValUnit', 'Date',
                    'DimNo', 'ValNo', 'ShotNo', 'DimSize']
        for need_key in need_keys:
            if need_key not in parameters.keys():
                raise ValueError('There is no '+ need_key + ' property in ' + filename)
    """
    Next, we load [Data] part of file.
    """
    # temporary data
    tmpdata = np.loadtxt(filename, comments='#', delimiter=',')
    # storing and reshape dims (dict)
    coords = OrderedDict()
    for i in range(len(parameters['DimName'])):
        d = tmpdata[:,i].reshape(parameters['DimSize'])
        coords[parameters['DimName'][i]] = \
            np.swapaxes(d, 0, i).flatten(order='F')[:parameters['DimSize'][i]]

    # xr.DataSet that will be created by this method.
    result = OrderedDict()
    for i in range(len(parameters['ValName'])):
        result[parameters['ValName'][i]] = xr.DataArray(
                data = tmpdata[:,i+len(parameters['DimName'])]\
                        .reshape(parameters['DimSize']),
                dims = parameters['DimName'],
                coords = coords,
                name = parameters['ValName'][i],
                attrs = {'Unit': parameters['ValUnit'][i]})

    attrs = OrderedDict()
    for key, item in parameters.items():
        # remove unnecessary parameters (to avoid duplicity)
        if key not in ['DimName', 'DimNo', 'ValName', 'ValNo', 'DimSize',
                       'DimUnit', 'ValUnit']:
            attrs[key] = item
    attrs['comments'] = comments

    ds = EGdata(result, coords=coords, attrs=attrs)
    # append attrs to coords manually
    for i in range(len(parameters['DimName'])):
        ds.coords[parameters['DimName'][i]].attrs['Unit'] = \
                                                        parameters['DimUnit'][i]
    return ds

def dump(dataset, filename, fmt='%.6e', NAME=None, ShotNo=None):
    """
    Save xarray.Dataset to file.

    parameters:
    - dataset: xarray.Dataset object.
        To make the file compatibile to eg file, the following information is necessary, ['NAME', 'ShotNo']
        To add these attributes to xarray.Dataset, call
        >>> dataset.attrs['NAME'] = 'some_name'
    - filename: path to file
    - fmt: format of the values. Same to np.savetxt. See
        https://docs.scipy.org/doc/numpy/reference/generated/numpy.savetxt.html
        for the detail.
    """
    obj = dataset.copy(deep=True)
    # Make sure some necessary parameters are certainly stored
    if NAME is None:
        if 'NAME' not in obj.attrs.keys():
            raise ValueError('There is no '+ NAME + ' property in ' + filename +\
                        '. Please provide NAME argument')
        else:
            NAME = obj.attrs['NAME']
    obj.attrs['NAME'] = NAME

    if ShotNo is None:
        if 'ShotNo' not in obj.attrs.keys():
            raise ValueError('There is no '+ ShotNo + ' property in ' + filename +\
                        '. Please provide NAME argument')
        else:
            ShotNo = obj.attrs['ShotNo']
    obj.attrs['ShotNo'] = ShotNo

    # add some attributes
    obj.attrs['DimName'] = list(obj.dims)
    obj.attrs['DimNo']   = len(obj.dims)
    obj.attrs['DimUnit'] = [obj.coords[d].attrs['Unit']
                            if 'Unit' in obj.coords[d].attrs.keys() else ''
                            for d in obj.dims]
    obj.attrs['DimSize'] = [len(obj.coords[d]) for d in obj.dims]
    obj.attrs['ValName'] = list(obj.data_vars.keys())
    obj.attrs['ValNo']   = len(obj.data_vars.keys())
    obj.attrs['ValUnit'] = [c.attrs['Unit'] if 'Unit' in c.attrs.keys() else ''
                                for key,c in obj.data_vars.items()]
    obj.attrs['Date']    = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    # --- A simple method to convert list to string ----
    def _list_to_strings(slist):
        # convert from list_of_strings to string
        string = ""
        # a simple method to make string from string or integer
        def _str(s):
            return '\''+s+'\'' if isinstance(s, str) else str(s)

        for i in range(len(slist)-1):
            string += _str(slist[i])+', '
        string += _str(slist[-1])
        return string
    # ---- end of this method ---

    # prepare the header
    # main parameters
    header = "[Parameters]\n"
    for key in ['NAME', 'ShotNo', 'Date', 'DimNo', 'DimName', 'DimSize', 'DimUnit',
                'ValNo', 'ValName', 'ValUnit']:
        item = obj.attrs[key]
        if isinstance(item, list):
            header += key + " = " + _list_to_strings(item) +"\n"
        else:
            header += key + " = " + str(item) +"\n"
        del obj.attrs[key] # remove already written entries.

    # other parameters
    for key, item in obj.attrs.items():
        if key is not 'comments':
            header += key + " = " + str(item) +"\n"

    # comments
    header += "\n[comments]\n"
    if 'comments' in obj.attrs.keys():
        for key, item in obj.attrs['comments'].items():
            if isinstance(item, list):
                item = _list_to_strings(item)
            header += key + " = " + str(item) +"\n"
    # data start
    header += "\n[data]"

    #---  prepare 2d data to write into file ---
    data = []
    dimsize = [len(obj.coords[key]) for key in obj.dims]
    # prepare coords.
    for i, key in zip(list(range(len(obj.dims))), obj.dims):
        # expand dims to match the data_vars shape
        coord = obj.coords[key]
        for j in range(len(obj.dims)):
            if i != j:
                coord = np.expand_dims(coord, axis=j)
        # tile the expanded dims
        shape = deepcopy(dimsize)
        shape[i] = 1
        data.append(np.tile(coord, shape).flatten(order='C'))
    # append data_vars
    for key, item in obj.data_vars.items():
        data.append(item.values.flatten(order='C'))

    # write to file
    np.savetxt(filename, np.stack(data, axis=0).transpose(), header=header,
               delimiter=',', fmt=fmt)


class EGdata(xr.Dataset):
    """
    Object that stores eg-data.
    This methods inherites from xr.Dataset.

    Coordinate data is stored as OrderedDict
    >>> eg_data.coords

    To see what coordinates is stored,
    >>> eg_data.coords.keys()

    To access the particular coordinate, e.g. TIME,
    >>> eg_data.coords['TIME']
    or simply
    >>> eg_data['TIME']

    To see what values are stored,
    >>> eg_data.keys()
    which returns the list of names including coordinates.

    To access the data,
    >>> eg_data['... a key of the value']

    Full list of methods can be found in
    http://xarray.pydata.org/en/stable/api.html#dataarray
    """

    def __getattribute__(self, key):
        """
        Overwrite __getattribute__ to keep the backcompatibility
        """
        o = object.__getattribute__(self, key)
        # Officially supported properties
        if key in ['NAME', 'ShotNo', 'DimUnit', 'ValUnit']:
            return self.attrs[key]
        return o

    @property
    def dim(self):
        warnings.warn('\'dim\' property is deprecated. Use \'coords\' or [] operator instead.\n' +
        'This method will return xarray.DataArray rather than np.array',
                                            DeprecationWarning, stacklevel=2)
        rt = OrderedDict()
        for key, item in self.coords.items():
            rt[key] = item.values
        return rt

    @property
    def val(self):
        warnings.warn('\'val\' property is deprecated. Use [] operator instead.\n'+
        'This method will return xarray.DataArray rather than np.array',
                                            DeprecationWarning, stacklevel=2)
        rt = OrderedDict()
        for key, item in self.data_vars.items():
            rt[key] = item.values
        return rt

    @property
    def comments(self):
        warnings.warn('\'comments\' property is deprecated. Access via self.atttrs[\'comments\'].',
                                            DeprecationWarning, stacklevel=2)
        return self.attrs['comments']

    def val_property(self):
        """
        Warning: This method is deprecated
        Return ordered_dict that connects ValName and ValUnit
        """
        warnings.warn('\'val_property\' method is deprecated. Use print(data) instead',
                                            DeprecationWarning, stacklevel=2)
        prop = OrderedDict()
        for key, item in self.data_vars.items():
            prop[key] = item.attrs['Unit']
        return prop

    def dim_property(self):
        """
        Warning: This method is deprecated
        Return ordered_dict that connects DimName and DimUnit
        """
        warnings.warn('\'dim_property\' method is deprecated. Use print(data) instead',
                                            DeprecationWarning, stacklevel=2)
        prop = OrderedDict()
        for key, item in self.coords.items():
            prop[key] = item.attrs['Unit']
        return prop
