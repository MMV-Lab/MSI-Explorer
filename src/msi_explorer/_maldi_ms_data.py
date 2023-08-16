"""
Module for the definition of the class Maldi_MS

Imports
-------
numpy, matplotlib.pyplot, json, pyimzml.ImzMLParser

Exports
-------
Maldi_MS
"""

# Copyright © Peter Lampen, ISAS Dortmund, 2023
# (07.02.2023)

import numpy as np
import matplotlib.pyplot as plt
import json
import os
from pyimzml.ImzMLParser import ImzMLParser, getionimage, _bisect_spectrum
from bisect import bisect_left, bisect_right

class Maldi_MS():
    """
    A class to store Maldi-MS data.
    
    Attributes
    ----------
    p : class ImzMLParser
        This is the result of the method ImzMLParser('NN.imzML')
    spectra : list
        A list of sublists containing two ndarrays: m/z and intensity
    norm_spectra : list
        A list of sublists containing normalized spectra
    is_norm : boolean
        re there normalized spectra?
    coordinates : list
        A list of tuples containing the coordinates (x, y, z)
    metadata : dict
        A nested dictionary with the metadata of the measurement
    num_spectra : int
        Number of spectra in the list spectra

    Methods
    -------
    __init__(filename:str)
        class constructor
    check_i(i:int)
        check whether i is in the interval [0, num_spectra-1]
    normalize(self, norm:str, mz0:float = 256.777, tol:float = 0.003)
        normalize the spectra by different methods: tic, rms, median, peak
    get_spectrum(i:int)
        get a list with m/z and intensity of spectrum[i]
    get_all_spectra()
        get a list with all spectra
    plot_spectrum(i:int)
        plot spectrum[i] with matplotlib.pyplot
    get_num_spectra()
        get the number of spectra
    get_index(y:int, x:int)
        get the index of the spectrum at coordinates (x, y, 1)
    get_coordinates(i:int)
        get the coordinates (x, y, 1) of spectrum[i]
    get_ion_image(mz:float, tol:float)
        get a 2D ndarray with an ion image at m/z +/- tol
    get_tic()
        get the total ion current (tic) of all spectra
    get_metadata_json()
        get a string of the metadata in JSON format
    get_metadata()
        get a dictionary with selected metadata
    getionimage_norm(self, p, mz_value, tol=0.1, z=1, reduce_func=sum)
        Get an image representation of the intensity distribution
        of the ion with specified m/z value.
    """


    def __init__(self, filename:str):
        """
        class constructor
        
        Parameters
        ----------
        filename : str
            Path and file name of the imzML file
        """

        if not os.path.isfile(filename):        # Check if the file exists
            raise FileNotFoundError(filename, 'don\'t exist')

        p = ImzMLParser(filename)
        self.p = p
        self.spectra = []           # empty list
        self.norm_spectra = []
        self.is_norm = False
        self.norm_type = 'original' # Lennart
        self.coordinates = []

        for i, (x, y, z) in enumerate(p.coordinates):
            mz, intensities = p.getspectrum(i)
            self.spectra.append([mz, intensities])      # list of lists
            self.coordinates.append((x, y, z))          # list of tuples

        self.metadata = p.metadata.pretty()             # nested dictionary
        self.num_spectra = len(self.coordinates)        # number of spectra


    def check_i(self, i:int):
        """
        check whether index i is in the interval [0, num_spectra-1]

        Parameter
        ---------
        i : int
            Index of a spectrum

        Returns
        -------
        int
            i if 0 <= i <= num_spectra-1
            0 if i < 0
            num_spectra-1 if i >= num_spectra
        """

        try:
            i = int(i)
        except BaseException as err:
            print('Error:', err)
            i = 0

        # Is 0 <= i < self.num_spectra?
        if i < 0: i = 0
        elif i >= self.num_spectra:
            i = self.num_spectra - 1
        return i


    def normalize(self, norm:str, mz0:float = 256.777, tol:float = 0.003):
        self.norm_spectra = []
        self.norm_type = norm # Lennart
        if norm == 'original': # Lennart
            self.is_norm = False
        elif norm == 'tic':               # Total ion current = Mean
            for spectrum in self.spectra:
                mz = spectrum[0]
                intensities = np.copy(spectrum[1])

                filter = intensities != 0.0
                intensities2 = intensities[filter]
                tic = np.mean(intensities2)

                intensities /= tic
                self.norm_spectra.append([mz, intensities])
            self.is_norm = True
        elif norm == 'rms':               # Root mean square = Vector norm
            for spectrum in self.spectra:
                mz = spectrum[0]
                intensities = np.copy(spectrum[1])

                filter = intensities != 0.0
                intensities2 = intensities[filter]
                square1 = np.square(intensities2)
                mean1 = np.mean(square1)
                rms = np.sqrt(mean1)

                intensities /= rms
                self.norm_spectra.append([mz, intensities])
            self.is_norm = True
        elif norm == 'median':
            for spectrum in self.spectra:
                mz = spectrum[0]
                intensities = np.copy(spectrum[1])

                filter = intensities != 0.0
                intensities2 = intensities[filter]
                median1 = np.median(intensities2)

                intensities /= median1
                self.norm_spectra.append([mz, intensities])
            self.is_norm = True
        elif norm == 'peak':
            for spectrum in self.spectra:
                mz = spectrum[0]
                intensities = np.copy(spectrum[1])

                # First step: define an interval on the abscissa
                filter1 = mz >= (mz0 - tol)
                filter2 = mz <= (mz0 + tol)
                filter3 = np.logical_and(filter1, filter2)

                # Second step: calculate a factor for normalization
                if np.any(filter3):         # peak found
                    maximum = intensities[filter3].max()
                    if maximum > 0.0:
                        factor = 100.0 / maximum
                    else:                   # only zeros found
                        factor = 0.0
                else:                       # nothing found
                    factor = 0.0

                # Third step: normalize the spectrum
                intensities *= factor
                self.norm_spectra.append([mz, intensities])
            self.is_norm = True
            self.norm_type += f" {mz0}"


    def get_spectrum(self, i:int):
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

        if self.is_norm:
            return self.norm_spectra[i]
        else:
            return self.spectra[i]


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
        if self.is_norm:
            return self.norm_spectra
        else:
            return self.spectra


    def plot_spectrum(self, i:int):
        """
        plot spectrum[i] with matplotlib.pyplot

        Parameter
        ---------
        i : int
            index of spectrum[i]
        """

        spectrum = self.get_spectrum(i)
        mz, intensities = spectrum
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

        return self.num_spectra


    def get_index(self, y:int, x:int):
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
            i = self.coordinates.index((x, y, 1))
            return i
        except BaseException:
            return -1


    def get_coordinates(self, i:int):
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
        return self.coordinates[i]


    def get_ion_image(self, mz:float, tol:float = 0.1):
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
        if self.is_norm:
            return self.getionimage_norm(self.p, mz, tol)
        else:
            return getionimage(self.p, mz, tol)


    def get_tic(self):
        """
        get the total ion current (tic) of all spectra

        Returns
        -------
        numpy.ndarray
            total ion current of all spectra
        """

        # (17.02.2023)
        n = self.num_spectra
        tic = np.zeros(n)

        for i, spectrum in enumerate(self.spectra):
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

        return json.dumps(self.metadata, sort_keys=False, indent=4)


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

        meta = self.metadata
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


    def getionimage_norm(self, p, mz_value, tol=0.1, z=1, reduce_func=sum):
        """
        Reference: https://github.com/alexandrovteam/pyimzML

        Get an image representation of the intensity distribution
        of the ion with specified m/z value.

        By default, the intensity values within the tolerance region are summed.

        :param p:
            the ImzMLParser (or anything else with similar attributes) for the desired dataset
        :param mz_value:
            m/z value for which the ion image shall be returned
        :param tol:
            Absolute tolerance for the m/z value, such that all ions with values
            mz_value-|tol| <= x <= mz_value+|tol| are included. Defaults to 0.1
        :param z:
            z Value if spectrogram is 3-dimensional.
        :param reduce_func:
            the bahaviour for reducing the intensities between mz_value-|tol| and mz_value+|tol| to a single value. Must
            be a function that takes a sequence as input and outputs a number. By default, the values are summed.

        :return:
            numpy matrix with each element representing the ion intensity in this
            pixel. Can be easily plotted with matplotlib
        """
        tol = abs(tol)
        im = np.zeros((self.p.imzmldict["max count of pixels y"], \
            self.p.imzmldict["max count of pixels x"]))
        for i, (x, y, z_) in enumerate(self.p.coordinates):
            if z_ == 0:
                UserWarning("z coordinate = 0 present, if you're getting blank images set getionimage(.., .., z=0)")
            if z_ == z:
                mzs, ints = map(lambda x: np.asarray(x), self.get_spectrum(i))
                min_i, max_i = _bisect_spectrum(mzs, mz_value, tol)
                im[y - 1, x - 1] = reduce_func(ints[min_i:max_i+1])
        return im
