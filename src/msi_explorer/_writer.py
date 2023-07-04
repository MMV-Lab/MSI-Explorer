from __future__ import annotations
from qtpy.QtWidgets import QFileDialog, QMessageBox

#from typing import TYPE_CHECKING, Any, List, Sequence, Tuple, Union
import csv

"""if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]"""

def save_dialog(parent, filetype):
    """
    Opens a dialog to select a file to save to
    
    Parameters
    ----------
    parent : QWidget
        Parent widget for the dialog
    filetype : str
        Only files of this filetype will be displayed
        
    Returns
    -------
    str
        Path of the selected file
    """
    dialog = QFileDialog()
    filepath = dialog.getSaveFileName(parent,filter = filetype)
    return filepath

def write_metadata(path, data):
    """
    Writes the metadata to disk
    
    Parameters
    ----------
    path : str
        Path to save the metadata to
    data : list
        Metadata to be saved
    """
    file = open(path, 'w', newline = '')
    writer = csv.writer(file)
    for line in data:
        writer.writerow(line)
    #writer.writerows(data)
    file.close()
    
def create_new_database(path):
    """
    Creates a template database file at the given path's location
    
    Parameters
    ----------
    path : str
        Path to write the new database to
    """
    file = open(path + "NewDatabase.csv", 'w', newline = '\n')
    writer = csv.writer(file)
    writer.writerow(["M/Z value", "Name", "Description"])
    file.close()
    msg = QMessageBox()
    msg.setWindowTitle("New Database created")
    msg.setText("New csv file has been created")
    msg.exec()
    

"""def write_single_image(path: str, data: Any, meta: dict) -> List[str]:
    ""Writes a single image layer""

    # implement your writer logic here ...

    # return path to any file(s) that were successfully written
    return [path]


def write_multiple(path: str, data: List[FullLayerData]) -> List[str]:
    ""Writes multiple layers of different types.""

    # implement your writer logic here ...

    # return path to any file(s) that were successfully written
    return [path]"""
