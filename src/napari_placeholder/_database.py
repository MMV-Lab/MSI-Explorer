from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QCheckBox, QPushButton

class DatabaseWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setLayout(QVBoxLayout())
        
        self.parent = parent
        
        ### QObjects
        # Label
        label_database = QLabel("database")
        
        # Checkboxes
        checkbox_database_1 = QCheckBox("database 1")
        checkbox_database_2 = QCheckBox("database 2")
        checkbox_database_3 = QCheckBox("database 3")
        
        # Buttons
        btn_add_database = QPushButton("Add")
        btn_delete_database = QPushButton("Delete")
        btn_confirm = QPushButton("Confirm")
        
        btn_add_database.clicked.connect(self._add_database)        
        btn_delete_database.clicked.connect(self._delete_database)        
        btn_confirm.clicked.connect(self._return_values)
        
        ### Organize objects via widgets
        data_frame = QFrame()
        data_frame.setLayout(QVBoxLayout())
        
        data_frame.setStyleSheet("border-width: 1;"
                                   "border-radius: 3;"
                                   "border-style: solid;"
                                   "border-color: rgb(10, 10, 10);"
                                   )
        
        data_frame.layout().addWidget(label_database)        
        data_frame.layout().addWidget(checkbox_database_1)
        data_frame.layout().addWidget(checkbox_database_2)
        data_frame.layout().addWidget(checkbox_database_3)
        
        buttons_widget = QWidget()
        buttons_widget.setLayout(QHBoxLayout())
        buttons_widget.layout().addWidget(btn_add_database)
        buttons_widget.layout().addWidget(btn_delete_database)
        buttons_widget.layout().addWidget(btn_confirm)
        
        data_frame.layout().addWidget(buttons_widget)
        
        self.layout().addWidget(data_frame)
        
    def _add_database(self):
        pass
    
    def _delete_database(self):
        pass
    
    def _return_values(self):
        self.parent.mzs = None
        self.close()