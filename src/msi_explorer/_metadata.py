from qtpy.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QLineEdit, QHBoxLayout, QPushButton
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
        
        label_key_1 = QLabel("Key 1")
        label_key_2 = QLabel("Key 2")
        label_key_3 = QLabel("Key 3")
        
        label_value_1 = QLabel("Value 1")
        label_value_2 = QLabel("Value 2")
        label_value_3 = QLabel("Value 3")
        
        # Buttons
        btn_export = QPushButton("Export")
        btn_save = QPushButton("Save")
        
        btn_export.clicked.connect(self._export)
        btn_save.clicked.connect(self._store_metadata)
        
        ### Organize objects via widgets
        self.data_frame = QFrame()
        self.data_frame.setLayout(QVBoxLayout())
        
        self.data_frame.setStyleSheet("border-width: 1;"
                                   "border-radius: 3;"
                                   "border-style: solid;"
                                   "border-color: rgb(10, 10, 10);"
                                   )
        
        header_frame = QWidget()
        header_frame.setLayout(QHBoxLayout())
        header_frame.layout().addWidget(label_key)
        header_frame.layout().addWidget(label_value)
        
        self.data_frame.layout().addWidget(header_frame)
        
        if not hasattr(parent, "metadata"):
            metadata = ms_object.get_metadata()
        else:
            metadata = parent.metadata
        
        for key in metadata:
            key_label = QLabel(key)
            value_label = QLabel(str(metadata[key]))
            
            frame = QWidget()
            frame.setLayout(QHBoxLayout())
            frame.layout().addWidget(key_label)
            frame.layout().addWidget(value_label)
            
            self.data_frame.layout().addWidget(frame)
        
        self.layout().addWidget(self.data_frame)
        self.layout().addWidget(btn_save)
        self.layout().addWidget(btn_export)
        
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
        parent_layout = self.layout().itemAt(0).widget().layout()
        for i in range(0, parent_layout.count() - 1):
            line = parent_layout.itemAt(i).widget().layout()
            key = line.itemAt(0).widget().text()
            value = line.itemAt(1).widget().text()
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
        value = QLineEdit()
        
        frame = QWidget()
        frame.is_empty = True
        frame.setLayout(QHBoxLayout())
        frame.layout().addWidget(key)
        frame.layout().addWidget(value)
        
        self.data_frame.layout().addWidget(frame)
        
        def mark_line_used():
            """
            Marks the line as not empty (even if the text has been removed again)
            """
            frame.is_empty = False
            
        key.textChanged.connect(mark_line_used)
        value.textChanged.connect(mark_line_used)
        key.textChanged.connect(self._check_for_empty_line)
        value.textChanged.connect(self._check_for_empty_line)

    def _check_for_empty_line(self):
        """
        Checks if the last line's [is_empty] property is True, otherwise calls [add_line]
        """
        layout_all_lines = self.layout().itemAt(0).widget().layout()
        last_line = layout_all_lines.itemAt(layout_all_lines.count() -1).widget()
        if not last_line.is_empty:
            self._add_line()
        
        