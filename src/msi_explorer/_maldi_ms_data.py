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
from pyimzml.ImzMLParser import ImzMLParser, getionimage

class Maldi_MS():
    """
    A class to store Maldi-MS data.
    
    Attributes
    ----------
    parser : class ImzMLParser
        This is the result of the method ImzMLParser('NN.imzML')
    spectra : list
        A list of lists containing two ndarrays: m/z and intensity
    coordinates : list
        A list of tuples containing the coordinates (x, y, z)
    samplepoints : list
        list of the indices of the spectra for the calculation of the mean
        spectrum
    metadata : dict
        A nested dictionary with the metadata of the measurement
    num_spectra : int
        Number of spectra in the list spectra

    Methods
    -------
    __init__(filename)
        class constructor
    check_i(i)
        check whether i is in the interval [0, num_spectra-1]
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
    """


    def __init__(self, filename):
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
        self.parser = p
        self.spectra = []           # empty list
        self.normalized_spectra = []
        self.normalized = False
        self.coordinates = []
        self.samplepoints = []      # sample points for the mean spectrum

        for i, (x, y, z) in enumerate(p.coordinates):
            mz, intensities = p.getspectrum(i)
            self.spectra.append([mz, intensities])      # list of lists
            self.coordinates.append((x, y, z))          # list of tuples

        self.metadata = p.metadata.pretty()             # nested dictionary
        self.num_spectra = len(self.coordinates)        # number of spectra


    def check_i(self, i):
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


    def normalize(self, norm_type):
        if type == 'tic':
            # calculate a factor for the intensities to set the total
            # ion current (tic) to np.median(tic)
            tic = self.get_tic()
            median = np.median(tic)
            quotient = tic / median
            factor = np.reciprocal(quotient)

            self.normalized_spectra = []
            for i, spectrum in enumerate(self.spectra):
                spectrum[1] *= factor[i]
                self.normalized_spectra.append(spectrum)

            self.normalized = True
        return self.normalized_spectra


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

        if self.normalized:
            return self.normalized_spectra[i]
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
        if self.normalized:
            return self.normalized_spectra
        else:
            return self.spectra


    def plot_spectrum(self, i):
        """
        plot spectrum[i] with matplotlib.pyplot

        Parameter
        ---------
        i : int
            index of spectrum[i]
        """

        i = self.check_i(i)

        if self.normalized:
            spectrum = self._normalized_spectrum[i]
        else:
            spectrum = self.spectra[i]

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

        return self.num_spectra


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
            i = self.coordinates.index((x, y, 1))
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
        return self.coordinates[i]


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
        return getionimage(self.parser, mz, tol)


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
