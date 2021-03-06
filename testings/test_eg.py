from __future__ import print_function
import numpy as np
import unittest
import xarray as xr
import os
from PyLHD import eg

class test_eg(unittest.TestCase):
    def test_load_parameters(self):
        eg_data = eg.load('testings/eg_example2d.txt')
        # Assert eg_data is xr.DataSet
        self.assertTrue(isinstance(eg_data, xr.Dataset))
        # Assert parameters
        self.assertTrue(eg_data.NAME == 'example-2d')
        self.assertTrue(eg_data.ShotNo == 6115)
        # Assert Dim
        self.assertTrue(list(eg_data.coords.keys()) == ['TIME','R'])
        self.assertTrue(len(eg_data.coords['TIME']) == 5)
        self.assertTrue(len(eg_data.coords['R']) == 3)
        self.assertTrue(eg_data.coords['TIME'].attrs['Unit'] == 's')
        self.assertTrue(eg_data.coords['R'].attrs['Unit'] == 'm')
        # Assert vals
        self.assertTrue(list(eg_data.data_vars.keys()) == ['a','b','c','d'])
        self.assertTrue(eg_data['a'].shape == (5,3))
        self.assertTrue(eg_data['b'].shape == (5,3))
        self.assertTrue(eg_data['a'].attrs['Unit'] == 's')
        self.assertTrue(eg_data['b'].attrs['Unit'] == 'm')
        # comments
        self.assertTrue(eg_data.comments['PHI'] == '3.5')
        self.assertTrue(eg_data.comments['PHIunit'] == '\'portNO\'')
        self.assertTrue(eg_data.comments['comments'] == '\'Be thickness = 7.5 micro m\'')

    # --- deprecated test ---
    def test_load_1d(self):
        eg_data = eg.load('testings/eg_example1d.txt')
        # Assert dimname
        self.assertTrue(list(eg_data.coords.keys()) == ['TIME'])
        # Assert valname
        self.assertTrue(list(eg_data.keys()) == ['TIME', 'a', 'b', 'c', 'd'])
        # Assert sizes
        self.assertTrue(eg_data['a'].shape == (5,))
        self.assertTrue(eg_data['TIME'].shape == (5,))
        # Assert axis
        self.assertTrue(np.allclose(eg_data['TIME'],
                                    [0.01,0.02,0.03,0.04,0.05]))
        # Assert values
        self.assertTrue(np.allclose(eg_data['a'],
                                    [0.1,0.2,0.3,0.4,0.5]))

    def test_load_1d_variation1(self):
        eg_data = eg.load('testings/eg_example1d_variation1.txt')
        # Assert dimname
        self.assertTrue(list(eg_data.coords.keys()) == ['TIME'])
        # Assert valname
        self.assertTrue(list(eg_data.keys()) == ['TIME', 'a', 'b', 'c', 'd'])
        # Assert sizes
        self.assertTrue(eg_data['a'].shape == (5,))
        self.assertTrue(eg_data['TIME'].shape == (5,))
        # Assert axis
        self.assertTrue(np.allclose(eg_data['TIME'],
                                    [0.01,0.02,0.03,0.04,0.05]))
        # Assert values
        self.assertTrue(np.allclose(eg_data['a'],
                                    [0.1,0.2,0.3,0.4,0.5]))

    def test_load_2d(self):
        eg_data = eg.load('testings/eg_example2d.txt')
        # Assert dimname
        self.assertTrue(list(eg_data.coords.keys()) == ['TIME', 'R'])
        # Assert valname
        self.assertTrue(list(eg_data.keys()) == ['TIME', 'R', 'a', 'b', 'c', 'd'])
        # Assert sizes
        self.assertTrue(eg_data['a'].shape == (5,3))
        self.assertTrue(eg_data['TIME'].shape == (5,))
        self.assertTrue(eg_data['R'].shape == (3,))
        # Assert axis
        self.assertTrue(np.allclose(eg_data['TIME'],
                                    [0.01,0.02,0.03,0.04,0.05]))
        self.assertTrue(np.allclose(eg_data['R'],
                                    [0.1,0.2,0.3]))
        # Assert values
        self.assertTrue(np.allclose(eg_data['a'],
                                    [[0.11,0.12,0.13],
                                     [0.21,0.22,0.23],
                                     [0.31,0.32,0.33],
                                     [0.41,0.42,0.43],
                                     [0.51,0.52,0.53]]))

    def test_prop(self):
        # test val_property and dim_property
        eg_data = eg.load('testings/eg_example1d.txt')
        val_prop = eg_data.val_property()
        for key in val_prop.keys():
            self.assertTrue(key in ['a','b','c','d'])
            self.assertTrue(val_prop[key] in ['s','m','V','V'])
        dim_prop = eg_data.dim_property()
        for key in dim_prop.keys():
            self.assertTrue(key in ['TIME'])
            self.assertTrue(dim_prop[key] in ['s'])


    def test_dump_1d(self):
        """ make sure dump method certainly works """
        filename = 'testfile'
        # make sure there is not file
        if os.path.exists(filename):
            os.remove(filename)
        # dump
        eg_data = eg.load('testings/eg_example1d.txt')
        eg.dump(eg_data, filename)
        # load again
        eg_data2 = eg.load(filename)
        # make sure these 2 are the same
        self.assertTrue(eg_data==eg_data2)
        if os.path.exists(filename):
            os.remove(filename)

    def test_dump_2d(self):
        """ make sure dump method certainly works """
        filename = 'testfile'
        # make sure there is not file
        if os.path.exists(filename):
            os.remove(filename)
        # dump
        eg_data = eg.load('testings/eg_example2d.txt')
        eg.dump(eg_data, filename)
        # load again
        eg_data2 = eg.load(filename)
        # make sure these 2 are the same
        self.assertTrue(eg_data==eg_data2)
        if os.path.exists(filename):
            os.remove(filename)
    '''
    def test_slice(self):
        # Make sure EGdata.__getitem__ certainly works.
        eg_data = eg.load('testings/eg_example2d.txt')
        eg_a_original = eg_data.val['a'].copy()
        eg_R_original = eg_data.dim['R'].copy()
        # crop by axis=0
        crop = eg_data[1:3]
        self.assertTrue(np.allclose(crop.dim['TIME'], [0.02,0.03]))
        self.assertTrue(np.allclose(crop.dim['R'], eg_data.dim['R']))
        self.assertTrue(np.allclose(crop.val['a'], eg_data.val['a'][1:3]))
        # make sure eg_data is not changed
        self.assertTrue(np.allclose(eg_R_original, eg_data.dim['R']))
        self.assertTrue(np.allclose(eg_a_original, eg_data.val['a']))

    def test_index(self):
        # Make sure EGdata.__getitem__ certainly works.
        eg_data = eg.load('testings/eg_example2d.txt')
        eg_a_original = eg_data.val['a'].copy()
        eg_R_original = eg_data.dim['R'].copy()
        # crop by axis=0
        crop = eg_data[[1,2]]
        self.assertTrue(np.allclose(crop.dim['TIME'], [0.02,0.03]))
        self.assertTrue(np.allclose(crop.dim['R'], eg_data.dim['R']))
        self.assertTrue(np.allclose(crop.val['a'], eg_data.val['a'][1:3]))
        # make sure eg_data is not changed
        self.assertTrue(np.allclose(eg_R_original, eg_data.dim['R']))
        self.assertTrue(np.allclose(eg_a_original, eg_data.val['a']))

    def test_dump_2d(self):
        #eg_data = eg.load('testings/eg_example2d.txt')
        #eg_data.dump('testings/eg_example2d_dump.txt')
        pass
    '''

    # --- deprecated test ---
    def test_load_1d_deprecated(self):
        eg_data = eg.load('testings/eg_example1d.txt')
        # Assert dimname
        self.assertTrue(list(eg_data.dim.keys()) == ['TIME'])
        # Assert valname
        self.assertTrue(list(eg_data.val.keys()) == ['a', 'b', 'c', 'd'])
        # Assert sizes
        self.assertTrue(eg_data.val['a'].shape == (5,))
        self.assertTrue(eg_data.dim['TIME'].shape == (5,))
        # Assert axis
        self.assertTrue(np.allclose(eg_data.dim['TIME'],
                                    [0.01,0.02,0.03,0.04,0.05]))
        # Assert values
        self.assertTrue(np.allclose(eg_data.val['a'],
                                    [0.1,0.2,0.3,0.4,0.5]))
    def test_load_1d_variation1_deprecated(self):
        eg_data = eg.load('testings/eg_example1d_variation1.txt')
        # Assert dimname
        self.assertTrue(list(eg_data.dim.keys()) == ['TIME'])
        # Assert valname
        self.assertTrue(list(eg_data.val.keys()) == ['a', 'b', 'c', 'd'])
        # Assert sizes
        self.assertTrue(eg_data.val['a'].shape == (5,))
        self.assertTrue(eg_data.dim['TIME'].shape == (5,))
        # Assert axis
        self.assertTrue(np.allclose(eg_data.dim['TIME'],
                                    [0.01,0.02,0.03,0.04,0.05]))
        # Assert values
        self.assertTrue(np.allclose(eg_data.val['a'],
                                    [0.1,0.2,0.3,0.4,0.5]))

    def test_load_2d_deprecated(self):
        eg_data = eg.load('testings/eg_example2d.txt')
        # Assert dimname
        self.assertTrue(list(eg_data.dim.keys()) == ['TIME', 'R'])
        self.assertTrue(type(eg_data.dim['TIME']) is np.ndarray)
        # Assert valname
        self.assertTrue(list(eg_data.val.keys()) == ['a', 'b', 'c', 'd'])
        self.assertTrue(type(eg_data.val['a']) is np.ndarray)
        # Assert sizes
        self.assertTrue(eg_data.val['a'].shape == (5,3))
        self.assertTrue(eg_data.dim['TIME'].shape == (5,))
        self.assertTrue(eg_data.dim['R'].shape == (3,))
        # Assert axis
        self.assertTrue(np.allclose(eg_data.dim['TIME'],
                                    [0.01,0.02,0.03,0.04,0.05]))
        self.assertTrue(np.allclose(eg_data.dim['R'],
                                    [0.1,0.2,0.3]))
        # Assert values
        self.assertTrue(np.allclose(eg_data.val['a'],
                                    [[0.11,0.12,0.13],
                                     [0.21,0.22,0.23],
                                     [0.31,0.32,0.33],
                                     [0.41,0.42,0.43],
                                     [0.51,0.52,0.53]]))
if __name__ == '__main__':
     unittest.main()
