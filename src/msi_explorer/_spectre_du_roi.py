import numpy as np
import vaex
from napari.qt.threading import thread_worker
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import Qt
import time

# Copyright © Peter Lampen, ISAS Dortmund, 2023
# (04.07.2023)


@thread_worker
def spectre_du_roi(maldi_ms, roi):
    """
    Calculation of the mean spectrum for a region of interest (ROI)

    Parameter
    ---------
    maldi_ms : object of the class Maldi_MS
        the object contains spectra, coordinates and metadata
    roi: list of tuples
        a list of tuples containing coordinates [(y1, x1), (y2, x2), ...]

    Returns
    -------
    list
        a list containing two 1D numpy arrays with m/z and intensities
        of the mean spectrum
    """
    
    start_time = time.time()        # start time
    QApplication.setOverrideCursor(Qt.WaitCursor)

    index = []              # Find the numbers of the spectra in the ROI
    for coord in roi:
        (y, x) = coord
        i = maldi_ms.get_index(y, x)
        if i >= 0:
            index.append(i)
    index.sort()

    if len(index) == 0:     # Is any spectrum in the ROI?
        raise ValueError('The ROI is empty')

    spectra = maldi_ms.get_all_spectra()

    spectra_df = [ vaex.from_arrays(mz=spectra[i][0], intens=spectra[i][1]) \
        for i in index ]            # convert all spectra to a DataFrame
    df = vaex.concat(spectra_df)    # build one big DataFrame

    df['mz'] = df.mz.round(4)       # round m/z to 4 decimal places
    # add up the intensities for equal m/z values
    df = df.groupby(df.mz, agg='sum', sort=True)

    mz = df.mz.values.to_numpy()    # convert the DataFrame to NumPy 1D arrays
    intens = df.intens_sum.values
    result = [mz, intens]

    stop_time = time.time()
    print('run time: %.2f seconds' % (stop_time - start_time))
    print('count = %d' % (df.count()))
    print('m/z = %.3f - %.3f' % (df.min(df.mz), df.max(df.mz)))
    print('intensity = %.1f - %9.4g' % (df.min(df.intens_sum), df.max(df.intens_sum)))

    QApplication.restoreOverrideCursor()
    return result
