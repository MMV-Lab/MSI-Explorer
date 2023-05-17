import multiprocessing
from multiprocessing import Pool
import numpy as np
import vaex
from _maldi_ms_data import Maldi_MS

# Copyright © Peter Lampen, ISAS Dortmund, 2023
# (17.05.2023)


global mean_spec1, mean_spec2

def mean_spec1(spectra):
    """
    This function is used to concatenate a large number of spectra to one
    vaex DataFrame

    Parameter
    ---------
    spectra : list
        list of spectra

    Returns
    -------
    vaex DataFrame
        a DataFrame containing the data points of all spectra in the list
    """

    spectrum = spectra[0]
    df = vaex.from_arrays(x=spectrum[0], y=spectrum[1]) # vaex DataFrame

    for spectrum in spectra[1:]:    # concatenate the other spectra
        df1 = vaex.from_arrays(x=spectrum[0], y=spectrum[1])
        df = df.concat(df1)         # connect two DataFrames
    return df


def mean_spec2(list1):
    """
    This function does the same as the function before, but instead of a list
    of spectra a list of vaex DataFrames is handed over

    Parameter
    ---------
    list1 : list
        list of vaex DataFrames

    Returns
    -------
    vaex DataFrame
        a DataFrame containing the data points of all spectra
    """

    df = list1[0]                   # vaex DataFrame

    for df1 in list1[1:]:           # concatenate the other spectra
        df = df.concat(df1)         # connect two DataFrames

    df['x'] = df.x.round(3)         # round m/z to 3 decimal places
    # add up the intensities for equal m/z values
    df = df.groupby(df.x, agg='sum', sort=True)
    return df


def get_true_mean_spec(maldi_ms)
    """
    Calculation of the true mean spectrum from all spectra of an .ibd file

    Parameter
    ---------
    maldi_ms : object of the class Maldi_MS
        the object contains spectra, coordinates and metadata

    Returns
    -------
    list
        a list containing m/z and the intensities of the mean spectrum
    """

    AMOUNT_OF_PROCESSES = np.maximum(1, int(multiprocessing.cpu_count() * 0.8))

    spectra0 = maldi_ms.get_all_spectra()
    n = maldi_ms.get_num_spec()
    k = n // 1000                           # last value for the loop
    m = n %  1000                           # division rest (Modulo)

    # Divide the list of spectra into smaller lists with 1000 spectra each
    spectra2 = []
    for i in range(0, k):
        start = i * 1000
        end = (i+1) * 1000
        spectra1 = spectra0[start:end]
        spectra2.append(spectra1)

    # The last list with the remaining spectra
    start = k * 1000
    end = start + m
    spectra1 = spectra0[start:end]
    spectra2.append(spectra1)

    with Pool(AMOUNT_OF_PROCESSES) as p:
        iterator = p.map(mean_spec1, spectra2)
    list1 = list(iterator)

    df = mean_spec2(list1)
    mz = df.x.values.to_numpy()     # convert the DataFrame to NumPy ndarrays
    intens = df.y_sum.values
    result = [mz, intens]
    return result
