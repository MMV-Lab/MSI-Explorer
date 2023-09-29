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

import copy
import numpy as np
from scipy.integrate import cumulative_trapezoid
import matplotlib.pyplot as plt
import json
import os
from pyimzml.ImzMLParser import ImzMLParser, getionimage, _bisect_spectrum
import time
from tqdm import tqdm

class Maldi_MS():
    """
    A class to store Maldi-MS data.
    
    Attributes
    ----------
    p : class ImzMLParser
        This is the result of the method ImzMLParser('NN.imzML')
    spectra : list
        A list of sublists containing two ndarrays: m/z and intensity
    new_spectra : list
        A list of sublists containing processed spectra
    is_norm : boolean
        are there normalized spectra?
    is_centroid : boolean
        are there centroid data
    coordinates : list
        A list of tuples containing the coordinates (x, y, z)
    metadata : dict
        A nested dictionary with the metadata of the measurement
    num_spectra : int
        Number of spectra in the list spectra

    Methods
    -------
    __init__(filename: str)
        class constructor
    check_i(i: int)
        check whether i is in the interval [0, num_spectra-1]
    get_spectrum(i: int)
        get a list with m/z and intensity of spectrum[i]
    get_all_spectra()
        get a list with all spectra
    plot_spectrum(i: int)
        plot spectrum[i] with matplotlib.pyplot
    get_num_spectra()
        get the number of spectra
    get_index(y: int, x: int)
        get the index of the spectrum at coordinates (x, y, 1)
    get_coordinates(i: int)
        get the coordinates (x, y, 1) of spectrum[i]
    get_ion_image(mz: float, tol: float)
        get a 2D ndarray with an ion image at m/z +/- tol
    plot_ion_image(self, image: ndarray):
        2D plot of an ion image
    get_metadata_json()
        get a string of the metadata in JSON format
    get_metadata()
        get a dictionary with selected metadata
    normalize(self, norm: str, mz0: float = 256.777, tol: float = 0.003)
        normalize the spectra by different methods: tic, rms, median, peak
    getionimage_new(self, p, mz_value, tol=0.1, z=1, reduce_func=sum)
        Get an image representation of the intensity distribution
        of the ion with specified m/z value.
    peak_filtering(self, factor: float = 0.01)
        remove small peaks < limit
    centroid_data(self)
        calculation of centroid data
    calculate_centroid_spectrum(self, spectrum: list)
        calculate a centroid spectrum from a profile spectrum
    check_centroid(self):
        is the spectrum in centroid mode?
    """

    def __init__(self, filename: str):
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
        self.new_spectra = []
        self.is_norm = False
        self.is_centroid = False
        self.norm_type = 'original' # Lennart
        self.coordinates = []

        for i, (x, y, z) in enumerate(p.coordinates):
            mz, intensities = p.getspectrum(i)
            self.spectra.append([mz, intensities])      # list of lists
            self.coordinates.append((x, y, z))          # list of tuples

        self.metadata = p.metadata.pretty()             # nested dictionary
        self.num_spectra = len(self.coordinates)        # number of spectra

    def check_i(self, i: int):
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

    def get_spectrum(self, i: int):
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

        if self.is_norm or self.is_centroid:
            return self.new_spectra[i]
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
        if self.is_norm or self.is_centroid:
            return self.new_spectra
        else:
            return self.spectra

    def plot_spectrum(self, i: int = 0):
        """
        plot spectrum[i] with matplotlib.pyplot

        Parameter
        ---------
        i : int
            index of spectrum[i]
        """

        if self.is_norm or self.is_centroid:
            mz, intensities = self.new_spectra[i]
        else:
            mz, intensities = self.spectra[i]

        fig, ax = plt.subplots()

        if self.is_centroid:
            ax.stem(mz, intensities, markerfmt='none')
        else:
            ax.plot(mz, intensities)

        title1 = 'Spectrum # %d' % (i)
        ax.set(xlabel = 'm/z', ylabel = 'Intensity', title = title1)
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

    def get_index(self, y: int, x: int):
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

    def get_coordinates(self, i: int):
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

    def get_ion_image(self, mz: float, tol: float = 0.1):
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
        if self.is_norm or self.is_centroid:
            return self.getionimage_new(self.p, mz, tol)
        else:
            return getionimage(self.p, mz, tol)

    def plot_ion_image(self, image):
        """
        plot the ion image calculateb by the function get_ion_image()

        Parameters
        ----------
        image : ndarray
            2D ion image
        """

        # (27.09.2023)
        fig, ax = plt.subplots()
        img = ax.imshow(image, interpolation='nearest', cmap='inferno')
        plt.colorbar(img)
        return fig

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

        if 'sf1' in meta['file_description']['source_files'].keys():
            d['name'] = meta['file_description']['source_files']['sf1']['name']
        elif 'SF1' in meta['file_description']['source_files'].keys():
            d['name'] = meta['file_description']['source_files']['SF1']['name']
        
        if 'scan1' in meta['referenceable_param_groups'].keys():
            d['filter string'] = \
                meta['referenceable_param_groups']['scan1']['filter string']
                
        if 'spectrum1' in meta['referenceable_param_groups'].keys() \
            and 'noise level' in meta['referenceable_param_groups']['spectrum1'].keys():
            d['noise level'] = \
                meta['referenceable_param_groups']['spectrum1']['noise level']
        
        if 'samples' in meta.keys():
            sample_keys = list(meta['samples'].keys())
            if len(sample_keys) == 1:
                d['samples'] = sample_keys[0]
            else:
                d['samples'] = sample_keys

        if 'scansettings1' in meta['scan_settings'].keys():
            d['max count x'] = \
                meta['scan_settings']['scansettings1']['max count of pixels x']
            d['max count y'] = \
                meta['scan_settings']['scansettings1']['max count of pixels y']
            d['pixel size x'] = \
                meta['scan_settings']['scansettings1']['pixel size (x)']
            d['pixel size y'] = \
                meta['scan_settings']['scansettings1']['pixel size y']
            print("case 1!")
        elif 'scanSettings0' in meta['scan_settings'].keys():
            d['max count x'] = \
                meta['scan_settings']['scanSettings0']['max count of pixels x']
            d['max count y'] = \
                meta['scan_settings']['scanSettings0']['max count of pixels y']
            d['pixel size x'] = \
                meta['scan_settings']['scanSettings0']['pixel size (x)']
            d['pixel size y'] = \
                meta['scan_settings']['scanSettings0']['pixel size y']
            print("case 2!")
        elif 'scan1' in meta['scan_settings'].keys():
            d['max count x'] = \
                meta['scan_settings']['scan1']['max count of pixels x']
            d['max count y'] = \
                meta['scan_settings']['scan1']['max count of pixels y']
            d['pixel size x'] = \
                meta['scan_settings']['scan1']['pixel size (x)']
            d['pixel size y'] = \
                meta['scan_settings']['scan1']['pixel size (x)']
            print("case 3!")
        elif 'scansetting1' in meta['scan_settings'].keys():
            d['max count x'] = \
                meta['scan_settings']['scansetting1']['max count of pixels x']
            d['max count y'] = \
                meta['scan_settings']['scansetting1']['max count of pixels y']
            d['pixel size x'] = \
                meta['scan_settings']['scansetting1']['pixel size (x)']
            d['pixel size y'] = \
                meta['scan_settings']['scansetting1']['pixel size y']
            print("case 4!")

        return d

    def normalize(self, norm: str, mz0: float = 256.777, tol: float = 0.003):
        """
        normalization of the spectra

        Parameters
        ----------
        norm : string
            'original', 'tic', 'rms', 'median' or 'peak'
        mz0 : float
            m/z value of the reference peak in Da
        tol : float
            tolerance of the m/z value in Da
        """
        # (18.07.2023)
        self.new_spectra = []
        self.norm_type = norm       # Lennart
        if norm == 'original':      # Lennart
            self.is_norm = False
        elif norm == 'tic':               # Total ion current = Mean
            for spectrum in self.spectra:
                mz = spectrum[0]
                intensities = np.copy(spectrum[1])

                filter = intensities != 0.0
                intensities2 = intensities[filter]
                tic = np.mean(intensities2)

                intensities /= tic
                self.new_spectra.append([mz, intensities])
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
                self.new_spectra.append([mz, intensities])
            self.is_norm = True
        elif norm == 'median':
            for spectrum in self.spectra:
                mz = spectrum[0]
                intensities = np.copy(spectrum[1])

                filter = intensities != 0.0
                intensities2 = intensities[filter]
                median1 = np.median(intensities2)

                intensities /= median1
                self.new_spectra.append([mz, intensities])
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
                self.new_spectra.append([mz, intensities])
            self.is_norm = True
            self.norm_type += f" {mz0}"

    def getionimage_new(self, p, mz_value, tol=0.1, z=1, reduce_func=sum):
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

    def peak_filtering(self, factor: float = 0.01):
        """
        remove small peaks < limit

        Parameters
        ----------
        factor : float
            factor to calculate the limit: limit = maximum * factor
        """

        # (31.08.2023)
        if self.is_norm or self.is_centroid:
            spectra = self.new_spectra
        else:
            spectra = self.spectra

        n = self.get_num_spectra()
        for i in range(0, n):
            spectrum = spectra[i]
            mz, intensities = spectrum

            # search for peaks >= limit
            maximum = intensities.max()
            limit = maximum * factor
            filter1 = intensities == 0.0
            filter2 = intensities >= limit
            filter3 = np.logical_or(filter1, filter2)

            # store peaks > limit and zeros
            mz2 = mz[filter3]
            intensities2 = intensities[filter3]
            spectra[i] = [mz2, intensities2]

    def centroid_data(self):
        """
        calculation of centroid data
        """
        
        # (26.09.2023)
        start_time = time.time()        # start time
        if self.is_norm:
            spectra = copy.deepcopy(self.new_spectra)
        else:
            spectra = self.spectra

        self.new_spectra = []

        for spectrum in tqdm(spectra):
            new_spectrum = self.calculate_centroid_spectrum(spectrum)
            self.new_spectra.append(new_spectrum)

        self.is_centroid = True
        stop_time = time.time()
        print('\nrun time: %.2f seconds' % (stop_time - start_time))

    def calculate_centroid_spectrum(self, spectrum: list):
        """
        calculate a centroid spectrum from a profile spectrum

        Parameters
        ----------
        spectrum : list
            A list containing two ndarrays: m/z and intensities

        Returns
        -------
        new_spectrum
            A list with the centroid data
        """
        
        # (26.09.2023)
        mz, intensities = spectrum
        quad_int = cumulative_trapezoid(intensities, x=mz, initial=0.0)
        # indeterminate integral across the spectrum
        mz_x_int = mz * intensities
        # product of m/z * intensity

        n = len(mz)
        i = 0           # counter for the data points in the profile spectrum
        j = 0           # counter for the peaks in the centroid spectrum
        ready = False
        mz2 = np.zeros(n)
        intensities2 = np.zeros(n)

        while ready != True:
            while (i < n) and (intensities[i] != 0.0):  # find the first 0
                i += 1
            while (i < n) and (intensities[i] == 0.0):  # find the last 0
                i += 1

            if i < n:
                start = i - 1       # last 0 before the peak
            else:
                ready = True        # end of the spectrum

            while (i < n) and (intensities[i] != 0.0):
                i += 1
            
            if i < n:
                end = i             # first 0 after the peak
            else:
                ready = True        # end of the spectrum

            if ready == False:
                new_intensity = quad_int[end] - quad_int[start]
                # determined integral over the peak
                sum_mz_x_int = np.sum(mz_x_int[start:end+1])
                # sum over m/z * intensity
                sum_int = np.sum(intensities[start:end+1])
                # sum of intensities
                
                new_mz = sum_mz_x_int / sum_int
                #print('start =', start, 'end =', end, 'mz2 =', mz2, 'intensity2 =', intensity2)
                mz2[j] = new_mz
                intensities2[j] = new_intensity
                j += 1

        return [mz2[0:j], intensities2[0:j]]

    def check_centroid(self):
        """
        Is the spectrum in centroid mode?

        Returns
        -------
        is_centroid : bool
            True: if the spectrum is in centroid mode
            False: else
        """

        # (29.09.2023)
        if self.is_centroid:
            return True
        else:
            n = self.num_spectra
            i = int(n / 2)
            spectrum = self.spectra[i]
            mz, intensities = spectrum
            min1 = np.min(intensities)
            median1 = np.median(intensities)

            if (min1 > 0.0) or ((min1 == 0) and (median1 == 0)):
                return True
            elif median1 > 0:
                return False
