from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QCheckBox, QPushButton
import csv, os

from ._writer import create_new_database

class DatabaseWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setLayout(QVBoxLayout())
        
        self.parent = parent
        self.db_directory = "src/napari_placeholder/databases/"
        
        ### QObjects
        # Label
        self.label_database = QLabel("database")
        
        # Checkboxes
        checkboxes = []
        for file in os.listdir(self.db_directory):
            checkboxes.append(QCheckBox(os.path.splitext(file)[0]))
        
        # Buttons
        btn_add_database = QPushButton("Add")
        btn_delete_database = QPushButton("Delete")
        btn_confirm = QPushButton("Confirm")
        
        btn_add_database.clicked.connect(self._add_database)        
        btn_delete_database.clicked.connect(self._delete_database)        
        btn_confirm.clicked.connect(self._return_values)
        
        ### Organize objects via widgets
        self.data_frame = QFrame()
        self.data_frame.setLayout(QVBoxLayout())
        
        self.data_frame.setStyleSheet("border-width: 1;"
                                   "border-radius: 3;"
                                   "border-style: solid;"
                                   "border-color: rgb(10, 10, 10);"
                                   )
        
        self.data_frame.layout().addWidget(self.label_database)
        for checkbox in checkboxes:
            self.data_frame.layout().addWidget(checkbox)
        
        self.buttons_widget = QWidget()
        self.buttons_widget.setLayout(QHBoxLayout())
        self.buttons_widget.layout().addWidget(btn_add_database)
        self.buttons_widget.layout().addWidget(btn_delete_database)
        self.buttons_widget.layout().addWidget(btn_confirm)
        
        self.data_frame.layout().addWidget(self.buttons_widget)
        
        self.layout().addWidget(self.data_frame)
        
    def _read_database_files(self):
        data_frame = self.data_frame
        new_data_frame = QFrame()
        new_data_frame.setLayout(QVBoxLayout())
        new_data_frame.setStyleSheet("border-width: 1;"
                                   "border-radius: 3;"
                                   "border-style: solid;"
                                   "border-color: rgb(10, 10, 10);"
                                   )
        new_data_frame.layout().addWidget(self.label_database)
        
        for file in os.listdir(self.db_directory):
            checkbox = QCheckBox(os.path.splitext(file)[0])
            new_data_frame.layout().addWidget(checkbox)
        #TODO: replace self.data_frame with new_dataframe, hide old widget
        
        
    def _add_database(self):
        create_new_database(self.db_directory)
        
    
    def _delete_database(self):
        pass
    
    def _return_values(self):
        mzs = []
        data = self.layout().itemAt(0).widget().layout()
        for i in range(1, data.indexOf(self.buttons_widget)):
            if data.itemAt(i).widget().isChecked():
                with open(self.db_directory+data.itemAt(i).widget().text() + ".csv", newline='') as csvfile:
                    database_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                    for row in database_reader:
                        mzs.append(row[0])
                        mzs.append(row[1])

        self.parent.mzs = mzs
        self.parent.update_mzs()
        self.close()
        
        
        
        