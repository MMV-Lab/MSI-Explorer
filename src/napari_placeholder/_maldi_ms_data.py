"""
Module for the definition of the class Maldi_MS

Imports
-------
numpy, matplotlib.pyplot, json, vaex, random, pyimzml.ImzMLParser

Exports
-------
Maldi_MS
"""

# Copyright © Peter Lampen, ISAS Dortmund, 2023
# (07.02.2023)

import numpy as np
import matplotlib.pyplot as plt
import json
import vaex
import time
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
    -samplepoints : list
        list of the indices of the spectra for the calculation of the mean
        spectrum
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
    get_all_spectra()
        get a list with all spectra
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
    pseudo_mean_spec(n=1000)
        calculate a mean spectrum for n spectra
    get_samplepoints(self)
        get an image with the sample points for the calculation of the mean
        spectrum
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
        self._spectra = list()      # empty list
        self._coordinates = list()
        self._samplepoints = list() # sample points for the mean spectrum
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


    def get_all_spectra(self):
        """
        get a list with all spectra

        Parameter
        ---------

        Returns
        -------
        list
            A list of lists
        """

        # (17.05.2023)
        return self._spectra


    def plot_spectrum(self, i):
        """
        plot spectrum[i] with matplotlib.pyplot

        Parameter
        ---------
        i : int
            index of spectrum[i]
        """

        i = self.check_i(i)
        spectrum = self._spectra[i]
        mz = spectrum[0]
        intensities = spectrum[1]
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

        for i, spectrum in enumerate(self._spectra):
            tic[i] = spectrum[1].sum()

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


    def pseudo_mean_spec(self, n=1000):
        """
        calculate a pseudo mean spectrum from n random spectra

        Parameters
        ----------
        n : int
            number of spectra, used to calculate a pseudo mean spectrum

        Returns
        -------
        list
            the pseudo mean spectrum in the format [mz, intensity]
        """

        # (02.03.2023, geändert: 06.06.2023)
        start_time = time.time()       # start time

        # choose n random spectra from 0 to _num_spectra - 1
        if n < self._num_spectra:
            index = range(self._num_spectra)
            index = random.sample(index, n)
            index.sort()
        else:
            index = range(self._num_spectra)

        self._samplepoints = index      # save the sample points

        spectra = self._spectra
        spectra_df = [ vaex.from_arrays(mz=spectra[i][0], intens=spectra[i][1]) \
            for i in index ]                # convert all spectra to a DataFrame
        df = vaex.concat(spectra_df)        # build one big DataFrame

        df['mz'] = df.mz.round(4)           # round m/z to 3 decimal places
        # add up the intensities for equal m/z values
        df = df.groupby(df.mz, agg='sum', sort=True)

        mz = df.mz.values.to_numpy()        # convert the df to NumPy ndarray
        intens = df.intens_sum.values
        spectrum = (mz, intens)

        stop_time = time.time()
        print('run time: %.2f seconds' % (stop_time - start_time))
        print('count = %d' % (df.count()))
        print('m/z = %.3f - %.3f' % (df.min(df.mz), df.max(df.mz)))
        print('intensity = %.1f - %9.4g' % (df.min(df.intens_sum), df.max(df.intens_sum)))

        return spectrum


    def get_samplepoints(self):
        """
        get an image with the sample points used for the calculation of the
        mean spectrum

        Returns
        -------
        numpy.ndarray
            ndarray showing the position fo the sample points
        """

        # (09.05.2023)
        # determine the size of the images from the metadata
        try:
            max_x = self._metadata['scan_settings']['scansettings1'] \
                ['max count of pixels x']
        except BaseException:
            max_x = 0

        try:
            max_y = self._metadata['scan_settings']['scansettings1'] \
                ['max count of pixels y']
        except BaseException:
            max_y = 0

        # create the image of size max_y * max_x
        # print('max_x =', max_x, 'max_y =', max_y)       # test output
        image = np.zeros((max_y, max_x), dtype=np.int32)
        # print('len_sp =', len(self._samplepoints))

        for index in self._samplepoints:
            (x, y, z) = self.get_coordinates(index)
            image[y-1, x-1] = 1
                
        return image
