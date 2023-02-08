from pyimzml.ImzMLParser import ImzMLParser
from napari_placeholder import Maldi_MS


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


def reader_function(filename):
    """Take a file name and return a Maldi_MS object.

    Parameters
    ----------
    filename : string or Path object to an .imzML file (in XML format)

    Returns
    -------
    Maldi_MS object
    """

    try:
        p = ImzMLParser(filename)
        # p = ImzMLParser(filename, include_spectra_metadata='full')
    except BaseException as err:
        print('Error:', err)

    return Maldi_MS(p)
