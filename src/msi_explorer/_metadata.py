from qtpy.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QLineEdit, QHBoxLayout, QPushButton, QTableWidget
from ._writer import write_metadata, save_dialog

class MetadataWindow(QWidget):
    """
    A (QWidget) window to supplement and export the metadata of the imzml file
    
    
    Attributes
    ----------
    data_frame : QFrame
        Container to hold the key/value pairs
    
    Methods
    -------
    export()
        Opens save dialog, calls writer
    compile_metadata()
        Compiles metadata from all lines and returns it
    add_line()
        Adds an empty line at the bottom
    check_for_empty_line()
        Checks if last line is empty
    """
    def __init__(self, ms_object, parent):
        """
        Parameters
        ----------
        ms_object
            The ms object holding the data from the ibd and imzml file
        parent
            The parent widget
        """
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.parent = parent
        
        ### QObjects
        # Label
        label_key = QLabel("Key")
        label_value = QLabel("Value")
        
        # Buttons
        btn_export = QPushButton("Export")
        btn_save = QPushButton("Save")
        
        btn_export.clicked.connect(self._export)
        btn_save.clicked.connect(self._store_metadata)
        
        ### Organize objects via widgets
        self.data_frame = QTableWidget()
        self.data_frame.setColumnCount(2)
        self.data_frame.setRowCount(1)
        self.data_frame.setCellWidget(0,0,label_key)
        self.data_frame.setCellWidget(0,1,label_value)
        self.row_index = 1
        
        if not hasattr(parent, "metadata"):
            metadata = ms_object.get_metadata()
        else:
            metadata = parent.metadata
        
        for key in metadata:
            key_label = QLabel(key)
            value_label = QLabel(str(metadata[key]))
            
            self.data_frame.setRowCount(self.data_frame.rowCount() + 1)
            self.data_frame.setCellWidget(self.row_index,0,key_label)
            self.data_frame.setCellWidget(self.row_index,1,value_label)
            self.row_index += 1
            
        self.layout().addWidget(self.data_frame)
        self.layout().addWidget(btn_save)
        self.layout().addWidget(btn_export)
        self.first_manual_row = self.row_index
        
        self._add_line()
        
    def _export(self):
        """
        Opens a Dialog, gets a filepath from the dialog.
        Calls metadata writer with [filepath] and [metadata]
        """
        metadata = self._compile_metadata()
        filepath = save_dialog(self, '*.csv')[0]
        try:
            write_metadata(filepath,metadata)
        except FileNotFoundError:
            return
    
    def _compile_metadata(self):
        """
        Reads metadata from all lines
        
        Returns
        -------
        list
            A list of tuples that holds key/value pairs of metadata
        """
        metadata = []
        for row in range(self.data_frame.rowCount()):
            key = self.data_frame.cellWidget(row, 0).text()
            value = self.data_frame.cellWidget(row, 1).text()
            if key == '' or value == '':
                continue
            metadata.append((key,value))
        return metadata
    
    def _store_metadata(self):
        """
        Writes metadata to the parent object to keep it persistent during the session
        """
        metadata = dict(self._compile_metadata())
        # remove the "Key : Value" entry
        del metadata[next(iter(metadata))]
        self.parent.metadata = metadata
    
    def _add_line(self):
        """
        Creates a new line with [is_empty] set to true, adds it to the [data_frame]
        """
        key = QLineEdit()
        #key.setPlaceholderText("Testkey")
        value = QLineEdit()
        #value.setPlaceholderText("Testvalue")
        self.data_frame.setRowCount(self.data_frame.rowCount() + 1)
        self.data_frame.setCellWidget(self.row_index,0,key)
        self.data_frame.setCellWidget(self.row_index,1,value)
        self.row_index += 1
        
        key.textChanged.connect(self._check_for_empty_line)
        value.textChanged.connect(self._check_for_empty_line)

    def _check_for_empty_line(self):
        """
        Checks if the last line's [is_empty] property is True, otherwise calls [add_line]
        """
        for row in range(self.first_manual_row, self.data_frame.rowCount()):
            if self.data_frame.cellWidget(row, 0).text() == '' and self.data_frame.cellWidget(row, 1).text() == '':
                return
        self._add_line()
        
        