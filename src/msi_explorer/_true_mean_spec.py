import numpy as np
import vaex
from napari.qt.threading import thread_worker
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import Qt
from ._maldi_ms_data import Maldi_MS
import time
import os

# Copyright © Peter Lampen, ISAS Dortmund, 2023
# (17.05.2023)


@thread_worker
def get_true_mean_spec(maldi_ms):
    """
    Calculation of the true mean spectrum from all spectra of an .ibd file

    Parameter
    ---------
    maldi_ms : object of the class Maldi_MS
        the object contains spectra, coordinates and metadata

    Returns
    -------
    list
        a list containing two 1D numpy arrays with m/z and the intensities
        of the mean spectrum
    """
    
    start_time = time.time()        # start time
    QApplication.setOverrideCursor(Qt.WaitCursor)

    spectra = maldi_ms.get_all_spectra()
    spectra_df = [ vaex.from_arrays(mz=spectrum[0], intens=spectrum[1]) \
        for spectrum in spectra ]   # convert all spectra to vaex DataFrames
    df = vaex.concat(spectra_df)    # build one big DataFrame from all spectra

    df['mz'] = df.mz.round(4)       # round m/z to 4 decimal places
    # add up the intensities for equal m/z values
    df = df.groupby(df.mz, agg='sum', sort=True)

    mz = df.mz.values.to_numpy()    # convert the DataFrame to NumPy nDArrays
    intens = df.intens_sum.values
    result = [mz, intens]

    stop_time = time.time()
    print('run time: %.2f seconds' % (stop_time - start_time))
    print('count = %d' % (df.count()))
    print('m/z = %.3f - %.3f' % (df.min(df.mz), df.max(df.mz)))
    print('intensity = %.1f - %9.4g' % (df.min(df.intens_sum), df.max(df.intens_sum)))
    
    QApplication.restoreOverrideCursor()
    return result
