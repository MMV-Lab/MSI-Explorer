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
        plt.show()

    def print_metadata(self):
        print(self.get_metadata())

    # def print_sf_metadata(self):
        # print(self._spectrum_full_metadata[0].pretty())
