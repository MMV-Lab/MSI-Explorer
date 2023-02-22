from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QCheckBox, QPushButton
import csv

class DatabaseWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setLayout(QVBoxLayout())
        
        self.parent = parent
        
        ### QObjects
        # Label
        label_database = QLabel("database")
        
        # Checkboxes
        checkbox_database_1 = QCheckBox("test")
        checkbox_database_2 = QCheckBox("Metabolite_database_ver1")
        checkbox_database_3 = QCheckBox("database 3")
        
        checkbox_database_1.setChecked(True)
        
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
        
        self.buttons_widget = QWidget()
        self.buttons_widget.setLayout(QHBoxLayout())
        self.buttons_widget.layout().addWidget(btn_add_database)
        self.buttons_widget.layout().addWidget(btn_delete_database)
        self.buttons_widget.layout().addWidget(btn_confirm)
        
        data_frame.layout().addWidget(self.buttons_widget)
        
        self.layout().addWidget(data_frame)
        
    def _add_database(self):
        pass
    
    def _delete_database(self):
        pass
    
    def _return_values(self):
        mzs = []
        data = self.layout().itemAt(0).widget().layout()
        for i in range(1, data.indexOf(self.buttons_widget)):
            if data.itemAt(i).widget().isChecked():
                with open("src/napari_placeholder/databases/"+data.itemAt(i).widget().text() + ".csv", newline='') as csvfile:
                    database_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                    for row in database_reader:
                        mzs.append(row[0])
                        mzs.append(row[1])

        self.parent.mzs = mzs
        self.parent.update_mzs()
        self.close()
        
        
        
        