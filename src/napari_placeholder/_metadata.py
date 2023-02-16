from qtpy.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QLineEdit, QHBoxLayout, QPushButton
from ._writer import write_metadata, save_dialog

class MetadataWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        
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
        
        btn_export.clicked.connect(self._export)
        
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
        
        temp_frame_1 = QWidget()
        temp_frame_1.setLayout(QHBoxLayout())
        temp_frame_1.layout().addWidget(label_key_1)
        temp_frame_1.layout().addWidget(label_value_1)
        
        self.data_frame.layout().addWidget(temp_frame_1)
        
        temp_frame_2 = QWidget()
        temp_frame_2.setLayout(QHBoxLayout())
        temp_frame_2.layout().addWidget(label_key_2)
        temp_frame_2.layout().addWidget(label_value_2)
        
        self.data_frame.layout().addWidget(temp_frame_2)
        
        temp_frame_3 = QWidget()
        temp_frame_3.setLayout(QHBoxLayout())
        temp_frame_3.layout().addWidget(label_key_3)
        temp_frame_3.layout().addWidget(label_value_3)
        
        self.data_frame.layout().addWidget(temp_frame_3)
        
        self.layout().addWidget(self.data_frame)        
        self.layout().addWidget(btn_export)
        
        self._add_line()
        
    def _export(self):
        metadata = self._compile_metadata()
        filepath = save_dialog(self, '*.csv')[0]
        try:
            write_metadata(filepath,metadata)
        except FileNotFoundError:
            return
    
    def _compile_metadata(self):
        metadata = []
        parent_layout = self.layout().itemAt(0).widget().layout()
        for i in range(0, parent_layout.count() - 1):
            line = parent_layout.itemAt(i).widget().layout()
            key = line.itemAt(0).widget().text()
            value = line.itemAt(1).widget().text()
            metadata.append((key,value))
        return metadata
    
    # Adds two lineedits for user to input key/value pair
    def _add_line(self):
        key = QLineEdit()
        value = QLineEdit()
        
        frame = QWidget()
        frame.is_empty = True
        frame.setLayout(QHBoxLayout())
        frame.layout().addWidget(key)
        frame.layout().addWidget(value)
        
        self.data_frame.layout().addWidget(frame)
        
        def mark_line_used():
            frame.is_empty = False
            
        key.textChanged.connect(mark_line_used)
        value.textChanged.connect(mark_line_used)
        key.textChanged.connect(self._check_for_empty_line)
        value.textChanged.connect(self._check_for_empty_line)

    # If last line is not empty add a new one
    def _check_for_empty_line(self):
        layout_all_lines = self.layout().itemAt(0).widget().layout()
        last_line = layout_all_lines.itemAt(layout_all_lines.count() -1).widget()
        if not last_line.is_empty:
            self._add_line()
        
        