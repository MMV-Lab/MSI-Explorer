from __future__ import annotations
import csv
from qtpy.QtWidgets import QFileDialog, QMessageBox


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
    filepath = dialog.getSaveFileName(parent, filter=filetype)
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
    file = open(path, "w", newline="")
    writer = csv.writer(file)
    for line in data:
        writer.writerow(line)
    file.close()


def create_new_database(path):
    """
    Creates a template database file at the given path's location

    Parameters
    ----------
    path : str
        Path to write the new database to
    """
    file = open(path + "NewDatabase.csv", "w", newline="\n")
    writer = csv.writer(file)
    writer.writerow(["M/Z value", "Name", "Description"])
    file.close()
    msg = QMessageBox()
    msg.setWindowTitle("New Database created")
    msg.setText("New csv file has been created")
    msg.exec()


def write_file(path, data, append=False, newline=True):
    if append:
        mode = "a"
    else:
        mode = "w"
    f = open(path, mode)
    f.write(f"{data}")
    if newline:
        f.write("\n")
    f.close()
