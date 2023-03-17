"""
Module for the definition of the class Maldi_MS

Imports
-------
numpy, matplotlib.pyplot, json, vaex, random, pyimzml.ImzMLParser

Exports
-------
Maldi_MS

Copyright © Peter Lampen, ISAS Dortmund, 2023
"""

# (07.02.2023)

import numpy as np
import matplotlib.pyplot as plt
import json
import vaex
# import time
import random
from pyimzml.ImzMLParser import ImzMLParser, getionimage

class Maldi_MS():
    """
    A class to store Maldi-MS data.
    
    Attributes
    ----------
    _parser : class ImzMLParser
        This is the result of the method ImzMLParser('NN.imzML')
    _spectra : list
        A list of lists containing two ndarrays: m/z and intensity
    _coordinates : list
        A list of tuples containing the coordinates (x, y, z)
    _metadata : dict
        A nested dictionary with the metadata of the measurement
    _num_spectra : int
        Number of spectra in the list _spectra

    Methods
    -------
    __init__(filename)
        class constructor
    check_i(i)
        check whether i is in the interval [0, _num_spectra-1]
    get_spectrum(i)
        get a list with m/z and intensity of spectrum[i]
    plot_spectrum(i)
        plot spectrum[i] with matplotlib.pyplot
    get_num_spec()
        get the number of spectra
    get_index(y, x)
        get the index of the spectrum at coordinates (x, y, 1)
    get_coordinates(i)
        get the coordinates (x, y, 1) of spectrum[i]
    get_ion_image(mz, tol)
        get a 2D ndarray with an ion image at m/z +/- tol
    get_tic()
        get the total ion current (tic) of all spectra
    get_metadata_json()
        get a string of the metadata in JSON format
    get_metadata()
        get a dictionary with selected metadata
    merge_two_spectra(spectrum1, ,spectrum2)
        merge two Maldi-MS spectra together
    calc_mean_spec(n=1000)
        calculate a mean spectrum for n spectra
    """


    def __init__(self, filename):
        """
        class constructor
        
        Parameters
        ----------
        filename : str
            Path and file name of the imzML file
        """

        try:
            p = ImzMLParser(filename)
            # p = ImzMLParser(filename, include_spectra_metadata='full')
        except BaseException as err:
            print('Error:', err)

        self._parser = p
        self._spectra = list()
        self._coordinates = list()
        for i, (x, y, z) in enumerate(p.coordinates):
            mz, intensities = p.getspectrum(i)
            self._spectra.append([mz, intensities])     # list of lists
            self._coordinates.append((x, y, z))         # list of tuples

        self._metadata = p.metadata.pretty()            # nested dictionary
        # self._spectrum_full_metadata = p.spectrum_full_metadata
        self._num_spectra = len(self._coordinates)      # number of spectra


    def check_i(self, i):
        """
        check whether index i is in the interval [0, _num_spectra-1]

        Parameter
        ---------
        i : int
            Index of a spectrum

        Returns
        -------
        int
            i if 0 <= i <= _num_spectra-1
            0 if i < 0
            _num_spectra-1 if i >= _num_spectra
        """

        try:
            i = int(i)
        except BaseException as err:
            print('Error:', err)
            i = 0

        # Is 0 <= i < self._num_spectra?
        if i < 0: i = 0
        elif i >= self._num_spectra:
            i = self._num_spectra - 1
        return i


    def get_spectrum(self, i):
        """
        get a list with m/z and intensity of spectrum[i]

        Parameter
        ---------
        i : int
            index of spectrum[i]

        Returns
        -------
        list
            A list of two ndarrays: m/z and Intensity of spectrum[i]
        """

        i = self.check_i(i)
        return self._spectra[i]


    def plot_spectrum(self, i):
        """
        plot spectrum[i] with matplotlib.pyplot

        Parameter
        ---------
        i : int
            index of spectrum[i]
        """

        i = self.check_i(i)
        spec = self._spectra[i]
        mz = spec[0]
        intensities = spec[1]
        plt.plot(mz, intensities)
        plt.xlabel('m/z')
        plt.ylabel('intensity')
        title1 = 'Spectrum # %d' % (i)
        plt.title(title1)
        plt.show()


    def get_num_spectra(self):
        """
        get the number of spectra

        Returns
        -------
        int
            the number of spectra
        """

        return self._num_spectra


    def get_index(self, y, x):
        """
        get the index of the spectrum at coordinates (x, y, 1)

        Parameters
        ----------
        y : int
        x : int
            coordinates x and y of the spectrum

        Returns
        -------
        int
            index i of spectrum at coordinates (x, y, 1)
            -1 if the coordinates are unknown
        """

        # Find the index (i) of a mass spectrum at the position (x, y, 1).
        # (21.02.2023)
        try:
            i = self._coordinates.index((x, y, 1))
            return i
        except BaseException:
            return -1


    def get_coordinates(self, i):
        """
        get the coordinates (x, y, 1) of spectrum[i]


        Parameter
        ---------
        i : int
            index of spectrum[i]

        Returns
        -------
        tuple
            the coordinates (x, y, 1) of spectrum[i]
        """

        i = self.check_i(i)
        return self._coordinates[i]


    def get_ion_image(self, mz, tol=0.1):
        """
        get a 2D numpy.ndarray with a single ion image at m/z +/- tol

        Parameters
        ----------
        mz : float
            m/z value
        tol : float
            tolerance of the m/z value

        Returns
        -------
        numpy.ndarray
            ndarray with an single ion image at given m/z +/- tol
        """

        # Export of an ion image for the value m/z +/- tol (10.02.2023)
        return getionimage(self._parser, mz, tol)


    def get_tic(self):
        """
        get the total ion current (tic) of all spectra

        Returns
        -------
        numpy.ndarray
            total ion current of all spectra
        """

        # (17.02.2023)
        n = self._num_spectra
        tic = np.zeros(n)

        for i, spec in enumerate(self._spectra):
            tic[i] = spec[1].sum()

        return tic


    def get_metadata_json(self):
        """
        get a string of the metadata in JSON format

        Returns
        -------
        str
            all metadata as a string in JSON format
        """

        return json.dumps(self._metadata, sort_keys=False, indent=4)


    # def print_sf_metadata(self):
        # print(self._spectrum_full_metadata[0].pretty())


    def get_metadata(self):
        """
        get a dictionary with selected metadata

        Returns
        -------
        dict
            dictionary with selected metadata
        """

        # Read the dictionary p.metadata.pretty() to extract some metadata.
        # (23.02.2023)

        meta = self._metadata
        d = dict()

        try:
            d['name'] = \
                meta['file_description']['source_files']['sf1']['name']
        except BaseException:
            pass                                # This path don't exist

        try:
            d['filter string'] = \
                meta['referenceable_param_groups']['scan1']['filter string']
        except BaseException:
            pass

        try:
            d['noise level'] = \
                meta['referenceable_param_groups']['spectrum1']['noise level']
        except BaseException:
            pass

        try:
            sample_keys = meta['samples'].keys()    # object of class dict_keys
            sample_keys = list(sample_keys)         # e.g. ['essen_kidney']
            if len(sample_keys) == 1:
                d['samples'] = sample_keys[0]
            else:
                d['samples'] = sample_keys
        except BaseException:
            pass

        try:
            d['max count x'] = \
                meta['scan_settings']['scansettings1']['max count of pixels x']
        except BaseException:
            pass

        try:
            d['max count y'] = \
                meta['scan_settings']['scansettings1']['max count of pixels y']
        except BaseException:
            pass

        try:
            d['pixel size x'] = \
                meta['scan_settings']['scansettings1']['pixel size (x)']
        except BaseException:
            pass

        try:
            d['pixel size y'] = \
                meta['scan_settings']['scansettings1']['pixel size y']
        except BaseException:
            pass

        """
        try:
            inst_id = meta['instrument_configurations'].keys()
            inst_id = list(inst_id)
            inst_id = inst_id[0]                # e.g. 'Q Exactive HF'
            d['wavelength'] = \
                meta['instrument_configurations'][inst_id]['components'][0]['wavelength']
        except BaseException:
            pass

        try:
            inst_id = meta['instrument_configurations'].keys()
            inst_id = list(inst_id)
            inst_id = inst_id[0]
            d['pulse energy'] = \
                meta['instrument_configurations'][inst_id]['components'][0]['pulse energy']
        except BaseException:
            pass

        try:
            inst_id = meta['instrument_configurations'].keys()
            inst_id = list(inst_id)
            inst_id = inst_id[0]
            d['pulse duration'] = \
                meta['instrument_configurations'][inst_id]['components'][0]['pulse duration']
        except BaseException:
            pass
        """

        return d


    def merge_two_spectra(self, spectrum1, spectrum2):
        """
        merge two Maldi-MS spectra together

        Parameters
        ----------
        spectrum1 : list
        spectrum2 : list
            two sapectra from _spectra in the format [mz, intensity]

        Returns
        -------
        list
            a list with the merged spectrum: [mz, intensity]
        """

        # Build a new mass spectrum from spectra 1 and 2 (14.02.2023)

        x1 = spectrum1[0]       # m/z values of the 1st spectrum
        y1 = spectrum1[1]       # intensities of the 1st spectrum
        x2 = spectrum2[0]
        y2 = spectrum2[1]
        x3 = np.array([])
        y3 = np.array([])
        n = len(x1)             # number of data points of the 1st spectrum
        m = len(x2)
        i, j = 0, 0

        while True:                     # infinite loop
            if x1[i] < x2[j]:           # start with the 1st spectrum
                x3 = np.append(x3, x1[i])
                y3 = np.append(y3, y1[i])
                i += 1
            elif x1[i] > x2[j]:         # start with the 2nd spectrum
                x3 = np.append(x3, x2[j])
                y3 = np.append(y3, y2[j])
                j += 1
            else:                       # add the intensities of both spectra
                x3 = np.append(x3, x1[i])
                y3 = np.append(y3, y1[i] + y2[j])
                i += 1
                j += 1

            if (i == n) and (j == m):           # ready
                break
            elif i == n:                        # end of the 1st spectrum
                x3 = np.append(x3, x2[j:m])     # the rest of the 2nd spec.
                y3 = np.append(y3, y2[j:m])
                break
            elif j == m:                        # end of the 2nd spectrum
                x3 = np.append(x3, x1[i:n])     # the rest of the 1st spec.
                y3 = np.append(y3, y1[i:n])
                break

        return [x3, y3]


    def calc_mean_spec(self, n=1000):
        """
        calculate a mean spectrum for n spectra

        Parameters
        ----------
        n : int
            number of spectra, used to calculate a mean spec

        Returns
        -------
        list
            the mean spectrum in the format [mz, intensity]
        """

        # (02.03.2023)
        # start = time.process_time()   # to stop the run time

        # choose n random spectra from 0 to _num_spectra - 1
        if n < self._num_spectra:
            index = range(self._num_spectra)
            index = random.sample(index, n)
        else:
            index = range(self._num_spectra)
            n = self._num_spectra

        # calculate a factor for the intensities to set the total ion current
        # (tic) to np.median(tic)
        tic = self.get_tic()
        median = np.median(tic)
        quotient = tic / median
        factor = np.reciprocal(quotient)

        # start with the first spectrum
        idx = index[0]
        spec = self._spectra[idx]
        intens = spec[1] * factor[idx]
        df = vaex.from_arrays(x=spec[0], y=intens)  # build a Vaex DataFrame

        for idx in index[1:]:           # concatenate the other spectra
            spec = self._spectra[idx]
            intens = spec[1] * factor[idx]
            df1 = vaex.from_arrays(x=spec[0], y=intens)
            df = df.concat(df1)         # connect two DataFrames

        df['x'] = df.x.round(3)         # round m/z to 3 decimal places
        df = df.groupby(df.x, agg='sum', sort=True)
        # add up the intensities for equal m/z values

        mz = df.x.values.to_numpy()     # convert the DataFrame to NumPy ndarray
        intens = df.y_sum.values
        spec = (mz, intens)

        # stop = time.process_time()
        # print('count =', df.count())  # test output
        # print('m/z =', df.min(df.x), '-', df.max(df.x))
        # print('run time:', stop - start, 'seconds')

        return spec
