# This is a class to store MALDI-MS data (m/z values and intensities)
# together with lots of metadata
import numpy as np
import matplotlib.pyplot as plt
import json
from pyimzml.ImzMLParser import getionimage

class Maldi_MS():
    def __init__(self, p):
        self._parser = p
        self._spectra = list()
        self._coordinates = list()
        for i, (x, y, z) in enumerate(p.coordinates):
            mzs, intensities = p.getspectrum(i)
            self._spectra.append([mzs, intensities])    # list of lists
            self._coordinates.append((x, y, z))         # list of tuples

        self._metadata = p.metadata.pretty()            # nested dictionary
        # self._spectrum_full_metadata = p.spectrum_full_metadata
        self._num_spectra = len(self._coordinates)      # number of spectra

    def check_i(self, i):
        # Is 0 <= i < self._num_spectra
        try:
            i = int(i)
        except BaseException as err:
            print('Error:', err)
            i = 0

        if i < 0: i = 0
        elif i >= self._num_spectra:
            i = self._num_spectra - 1
        return i

    def get_spectrum(self, i):
        i = self.check_i(i)
        return self._spectra[i]

    def get_index(self, y, x):
        try:
            i = self._coordinates.index((x, y, 1))
            return i
        except BaseException as err:
            print('Error:', err)
            return -1

    def get_coordinates(self, i):
        i = self.check_i(i)
        return self._coordinates[i]

    def get_metadata(self):
        return json.dumps(self._metadata, sort_keys=False, indent=4)

    def get_num_spectra(self):
        return self._num_spectra

    def get_ion_image(self, mz, tol=0.1):
        return getionimage(self._parser, mz, tol)

    def plot_spectrum(self, i):
        i = self.check_i(i)
        spec = self._spectra[i]
        mzs = spec[0]
        intensities = spec[1]
        plt.plot(mzs, intensities)
        plt.xlabel('m/z')
        plt.ylabel('intensity')
        title1 = 'Spectrum # %d' % (i)
        plt.title(title1)
        plt.show()

    def print_metadata(self):
        print(self.get_metadata())

    # def print_sf_metadata(self):
        # print(self._spectrum_full_metadata[0].pretty())

    def get_tic(self):
        # calculate the total ion current for all spectra
        n = self._num_spectra
        tic = np.zeros(n)

        for i, spec in enumerate(self._spectra):
            tic[i] = spec[1].sum()

        return tic

    def merge_two_spectra(self, spectrum1, spectrum2):
        # build a new spectrum from spectrum 1 and 2
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
