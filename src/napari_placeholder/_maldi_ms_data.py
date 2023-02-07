# This is a class to store MALDI-MS data (m/z values and intensities)
# together with lots of metadata
import numpy as np
import matplotlib.pyplot as plt
import json

class MaldiMS():
    def __init__(self, spec, coord, meta):
        self._spectra = spec
        self._coordinates = coord
        self._metadata = meta

    def get_spectrum(self, i):
        return self._spectra[i]

    def get_coordinates(self, i):
        return self._coordinates[i]

    def get_metadata(self):
        return json.dumps(self._metadata, sort_keys=False, indent=4)

    def plot_spectrum(self, i):
        spec = self._spectra[i]
        mzs = spec[0]
        intensities = spec[1]
        plt.plot(mzs, intensities)
        plt.show()

    def print_metadata(self):
        print(json.dumps(self._metadata, sort_keys=False, indent=4))
