"""
Module for the definition of the class Maldi_MS

Imports
-------
copy, numpy, scipy, matplotlib.pyplot, json, os, pyimzml.ImzMLParser, time,
numba

Exports
-------
Maldi_MS
"""

# Copyright © Peter Lampen, ISAS Dortmund, 2023, 2024
# (07.02.2023)

import copy
import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt
import json
import os
from pyimzml.ImzMLParser import ImzMLParser, getionimage, _bisect_spectrum
import time
from numba import jit

class Maldi_MS():
    """
    Class for storing and processing Maldi-MS data.
    
    Attributes
    ----------
    p : class ImzMLParser
        This is the result of the method ImzMLParser('NN.imzML')
    spectra : list
        A list of sublists containing two ndarrays: m/z and intensities
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
    get_num_spectra()
        get the number of spectra
    get_index(y: int, x: int)
        get the index of the spectrum at coordinates (x, y, 1)
    get_coordinates(i: int)
        get the coordinates (x, y, 1) of spectrum[i]
    get_spectrum(i: int)
        get a list with m/z and intensities of spectrum[i]
    get_all_spectra()
        get a list of sublists with all spectra
    plot_spectrum(i: int, fmt : str)
        plot spectrum[i] with matplotlib.pyplot
    get_ion_image(mz: float, tol: float)
        get a 2D ndarray with an ion image at m/z +/- tol
    plot_ion_image(image: ndarray)
        2D plot of an ion image
    get_metadata_json()
        get a string of the metadata in JSON format
    get_metadata()
        get a dictionary with selected metadata
    normalize(norm: str, mz0: float = 121.0444, tol: float = 0.003)
        normalize the spectra by different methods: tic, rms, median, peak
    getionimage_new(p, mz_value, tol=0.1, z=1, reduce_func=sum)
        Get an image representation of the intensity distribution
        of the ion with specified m/z value.
    get_percentile(percentage: float)
        calculate the percentile of the intensities for a given percentage
    noise_reduction(percentage: float = 0.1)
        remove small peaks < limit
    remove_hotspots(percentage: float = 99.0)
        cut all peaks with an intensity greater than the n% percentile
    check_centroid()
        is the spectrum in centroid mode?
    centroid_data()
        calculation of centroid data
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
            raise FileNotFoundError(-1, 'The file ' + filename + ' don\'t exist')

        parser = ImzMLParser(filename)
        self.p = parser
        self.spectra = []           # empty list
        self.new_spectra = []
        self.coordinates = []
        self.is_norm = False
        self.is_centroid = False
        self.norm_type = 'original' # Lennart

        for i, (x, y, z) in enumerate(parser.coordinates):
            mz, intensities = parser.getspectrum(i)
            self.spectra.append([mz, intensities])      # list of sublists
            self.coordinates.append((x, y, z))          # list of tuples

        self.metadata = parser.metadata.pretty()        # nested dictionary
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
            i if 0 <= i < num_spectra
            0 if i < 0
            num_spectra-1 if i >= num_spectra
        """

        try:
            i = int(i)
        except BaseException as err:
            print('Error:', err)
            i = 0

        # Is 0 <= i < self.num_spectra?
        if i < 0:
            i = 0
        elif i >= self.num_spectra:
            i = self.num_spectra - 1
        return i

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
            return self.coordinates.index((x, y, 1))
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

    def get_spectrum(self, i: int):
        """
        get a list with m/z and intensities for spectrum[i]

        Parameter
        ---------
        i : int
            index of spectrum[i]

        Returns
        -------
        list
            A list of two ndarrays: m/z and intensities for spectrum[i]
        """

        i = self.check_i(i)

        if self.is_norm or self.is_centroid:
            return self.new_spectra[i]
        else:
            return self.spectra[i]

    def get_all_spectra(self):
        """
        get a list of sublists with all spectra

        Returns
        -------
        list
            A list of sublists
        """

        # (17.05.2023)
        if self.is_norm or self.is_centroid:
            return self.new_spectra
        else:
            return self.spectra

    def plot_spectrum(self, i: int = 0, fmt: str = '-'):
        """
        plot spectrum[i] with matplotlib.pyplot

        Parameter
        ---------
        i : int
            index of spectrum[i]
        fmt : str
            line style or marker
        """

        if self.is_norm or self.is_centroid:
            mz, intensities = self.new_spectra[i]
        else:
            mz, intensities = self.spectra[i]

        fig, ax = plt.subplots()

        if self.is_centroid:
            ax.stem(mz, intensities, markerfmt='none')
        else:
            ax.plot(mz, intensities, fmt)

        coord = self.get_coordinates(i)
        title1 = 'Spectrum %s # %d' % (coord, i)
        ax.set(xlabel = 'm/z', ylabel = 'Intensity', title = title1)
        plt.show()

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
            2D ndarray with an single ion image at given m/z +/- tol
        """

        # (10.02.2023)
        try:
            if self.is_norm or self.is_centroid:
                return self.getionimage_new(self.p, mz, tol)
            else:
                return getionimage(self.p, mz, tol)
        except IndexError as exc:
            raise RuntimeError("Error: metadata is incorrect") from exc

    def plot_ion_image(self, image, mz: float):
        """
        plot the ion image calculated by the function get_ion_image()

        Parameters
        ----------
        image : ndarray
            2D ion image
        """

        # (27.09.2023)
        fig, ax = plt.subplots()
        img = ax.imshow(image, interpolation='nearest', cmap='inferno')
        title1 = 'm/z = %.4f Da' % (mz)
        ax.set(xlabel = 'x', ylabel = 'y', title = title1)
        plt.colorbar(img)
        #return fig

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


        d['max count x'] = self.p.imzmldict["max count of pixels x"]
        d['max count y'] = self.p.imzmldict["max count of pixels y"]
        if 'scansettings1' in meta['scan_settings'].keys():
            d['pixel size x'] = \
                meta['scan_settings']['scansettings1']['pixel size (x)']
            d['pixel size y'] = \
                meta['scan_settings']['scansettings1']['pixel size y']
            print("case 1!")
        elif 'scanSettings0' in meta['scan_settings'].keys():
            d['pixel size x'] = \
                meta['scan_settings']['scanSettings0']['pixel size (x)']
            d['pixel size y'] = \
                meta['scan_settings']['scanSettings0']['pixel size y']
            print("case 2!")
        elif 'scan1' in meta['scan_settings'].keys():
            d['pixel size x'] = \
                meta['scan_settings']['scan1']['pixel size (x)']
            d['pixel size y'] = \
                meta['scan_settings']['scan1']['pixel size (x)']
            print("case 3!")
        elif 'scansetting1' in meta['scan_settings'].keys():
            d['pixel size x'] = \
                meta['scan_settings']['scansetting1']['pixel size (x)']
            d['pixel size y'] = \
                meta['scan_settings']['scansetting1']['pixel size y']
            print("case 4!")

        return d

    def normalize(self, norm: str, mz0: float = 121.0444, tol: float = 0.003):
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

    def get_percentile(self, percentage: float):
        """
        calculate the percentile of the intensities for a given percentage

        Parameters
        ----------
        percentage : float or list of floats
            percentage for the percentilwe to compute

        Returns
        -------
        percentile : float or list of floats
            calculated percentile of the intensities
        """

        # (06.02.2024)
        if self.is_norm or self.is_centroid:
            spectra = self.new_spectra
        else:
            spectra = self.spectra

        intensities = [ d[1] for d in spectra ]
        all_intensities = np.concatenate(intensities)

        # Remove the zeros from the intensities
        if not self.is_centroid:
            mask = all_intensities != 0
            all_intensities = all_intensities[mask]

        percentile1 = np.percentile(all_intensities, percentage)
        return percentile1

    def noise_reduction(self, percentage: float = 0.01):
        """
        remove small peaks < limit

        Parameters
        ----------
        percentage : float
            percentage for the calculation of the percentile
        """

        # (31.08.2023, neu 23.02.2024)
        if self.is_norm or self.is_centroid:
            spectra = self.new_spectra
        else:
            spectra = self.spectra

        limit = self.get_percentile(percentage)
        print('Noise reduction: limit =', limit)

        n = len(spectra)
        for i in range(n):
            intens0 = spectra[i][1]
            intensities = np.copy(intens0)

            # search for peaks < limit
            filter1 = intensities != 0.0
            filter2 = intensities < limit
            filter3 = np.logical_and(filter1, filter2)
            intensities[filter3] = 0.0
            spectra[i][1] = intensities

    def remove_hotspots(self, percentage: float = 99.0):
        """
        cut all peaks with an intensity greater than the n% percentile
        """

        # (14.02.2024)
        if self.is_norm or self.is_centroid:
            spectra = self.new_spectra
        else:
            spectra = self.spectra

        limit = self.get_percentile(percentage)
        print('Hotspot removal: limit =', limit)

        n = len(spectra)
        for i in range(n):
            intens0 = spectra[i][1]
            intensities = np.copy(intens0)

            # search for hotspots
            filter = intensities > limit
            intensities[filter] = limit
            spectra[i][1] = intensities

        """
        intensities = [ d[1] for d in spectra ]
        all_intensities = np.concatenate(intensities)
        plt.hist(all_intensities, bins=24, log=True)
        plt.title('Histogram')
        plt.xlabel('Intensities')
        plt.ylabel('Frequency')
        """

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

    def centroid_data(self):
        """
        calculation of centroid data
        """

        # (26.09.2023)
        start_time1 = time.time()       # start time

        if self.is_norm:
            old_spectra = copy.deepcopy(self.new_spectra)
        else:
            old_spectra = self.spectra

        self.new_spectra = []
        for i, [mz, intensities] in enumerate(old_spectra):
            mask = intensities != 0     # search for values not equal to zero
            mask = mask.astype(int)     # convert bool to 1 and 0
            diff = np.diff(mask)

            start_indices = np.where(diff == 1)[0]      # find start and end indices
            end_indices   = np.where(diff == -1)[0] + 1

            if mask[0]:                 # Is the first or the last element == 1?
                start_indices = np.insert(start_indices, 0, 0)
            if mask[-1]:
                n = len(mz)
                end_indices = np.append(end_indices, n-1)
                
            quadrature = integrate.cumulative_trapezoid(intensities, x=mz, \
                initial=0.0)
            # indeterminate integral across the spectrum
            centroid_spectrum = centroid_numba(mz, intensities, quadrature, \
                start_indices, end_indices)
            self.new_spectra.append(centroid_spectrum)

        self.is_centroid = True
        stop_time1 = time.time()         # stop time
        print('Calculating centroid data. Run time = %g seconds for %d spectra' \
            % (stop_time1 - start_time1, self.num_spectra))


@jit(nopython=True)
def centroid_numba(mz, intensities, quadrature, start_indices, end_indices):
    """
    Calculate one centroid spectrum

    Parameters
    ----------
    mz : ndarray
        m/z values
    intensities : ndarray
        intensities of the m/z values
    quadreature : ndarray
        indeterminate integral across the spectrum
    start_indices : ndarray
        indices of the last m/z values before the peaks
    end_indices : ndarray
        indices of the first m/z value after the peak

    Returns
    -------
    [new_mz, new_intensities] : list of two ndarrays
        m/z values and intensities of the centroid spectrum
    """
    
    csum_mz_int = np.cumsum(mz * intensities)
    # cumulative sum over (m/z * intensity)
    csum_int = np.cumsum(intensities)
    # cumulative sum over all intensities

    new_mz = np.zeros(len(start_indices))
    new_intensities = np.zeros(len(start_indices))

    for i in range(len(start_indices)):
        start = start_indices[i]
        end = end_indices[i]
        sum_mz_int = csum_mz_int[end] - csum_mz_int[start]
        # sum over m/z * intensity from start to end
        sum_int = csum_int[end] - csum_int[start]
        # sum over the intensities from start to end

        new_mz[i] = sum_mz_int / sum_int
        new_intensities[i] = quadrature[end] - quadrature[start]

    return [new_mz, new_intensities]
