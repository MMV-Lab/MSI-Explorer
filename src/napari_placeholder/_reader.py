import numpy as np
from pyimzml.ImzMLParser import ImzMLParser
from _maldi_ms_data import MaldiMS


def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if not path.endswith(".imzML"):
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path and return a MaldiMS object.

    Parameters
    ----------
    path : string or Path object to an .imzML file (in XML format)

    Returns
    -------
    MaldiMS object
    """

    try:
        p = ImzMLParser(path)
    except BaseException as err:
        print('Error:', err)

    spectra = []
    coordinates = []
    for i, (x, y, z) in enumerate(p.coordinates):
        mzs, intensities = p.getspectrum(i)
        spectra += [[mzs, intensities]]     # list of lists
        coordinates += [(x, y, z)]          # list of tuples

    metadata = p.metadata.pretty()          # nested dictionary
    maldi_ms = MaldiMS(spectra, coordinates, metadata)

    return maldi_ms
