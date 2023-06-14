from msi_explorer import Maldi_MS
from qtpy.QtWidgets import QFileDialog

def open_dialog(parent, filetype = "", directory = ""):
    """
    Opens a dialog to select a file to open
    
    Parameters
    ----------
    parent : QWidget
        Parent widget for the dialog
    filetype : str
        Only files of this filetype will be displayed
    directory : str
        Opens view at the specified directory
        
    Returns
    -------
    str
        Path of the selected file
    """
    dialog = QFileDialog()
    filepath = dialog.getOpenFileName(parent, "Select imzML file",filter = filetype, directory = directory)[0]
    return filepath

def napari_get_reader(path):
    """
    Determines reader type for file(s) at [path]

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
    """
    Take a file name and return a Maldi_MS object.

    Parameters
    ----------
    filename : str
        Path to an .imzML file (in XML format)

    Returns
    -------
        Maldi_MS object
    """

    return Maldi_MS(filename)
