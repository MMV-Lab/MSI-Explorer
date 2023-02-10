from __future__ import annotations
from qtpy.QtWidgets import QFileDialog

#from typing import TYPE_CHECKING, Any, List, Sequence, Tuple, Union
import csv

"""if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]"""

def save_dialog(parent, filetype):
    dialog = QFileDialog()
    filepath = dialog.getSaveFileName(parent,filter = filetype)
    return filepath

def write_metadata(path, data):
    file = open(path, 'w', newline = '')
    writer = csv.writer(file)
    for line in data:
        writer.writerow(line)
    #writer.writerows(data)
    file.close()
    

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
