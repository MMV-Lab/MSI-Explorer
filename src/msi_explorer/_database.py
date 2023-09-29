import csv
import os
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QCheckBox, QPushButton

from ._writer import create_new_database, write_file
from ._reader import select_directory

class DatabaseWindow(QWidget):
    """
    A (QWidget) window to select databases from a directory and pass the
    values from those databases to its parent
    
    
    Attributes
    ----------
    parent : QWidget
        This widget's parent widget
    buttons_widget : QWidget
        Container to hold/position the buttons at the bottom of the widget
        
    Methods
    -------
    read_database_files()
        Reads database files, re-displays all databases for selection
    add_database()
        Adds a template database
    delete_database()
        Allows user to select file to delete
    return_values()
        Reads data from selected databases, sets data in parent widget and triggers update
    """
    def __init__(self, parent):
        """
        Parameters
        ----------
        parent : QWidget
            This widget's parent widget
        """
        super().__init__()
        self.setLayout(QVBoxLayout())
        
        self.parent = parent
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),"databases.conf")
        with open(self.config_file) as f:
            self.db_directory = f.readline()
        if self.db_directory == "":
            self.db_directory = f"{os.path.dirname(os.path.abspath(__file__))}/"
            
        self.hidden_databases_conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),"hidden_databases.conf")
            
        ### QObjects
        # Label
        self.label_database = QLabel("Databases")
        
        # Buttons
        btn_add_database = QPushButton("Add")
        btn_confirm = QPushButton("Confirm")
        btn_set_path = QPushButton("Set path")
        btn_hide_database = QPushButton("Hide")
        btn_show_all_databases = QPushButton("Show all")
        
        btn_add_database.clicked.connect(self._add_database)  
        btn_confirm.clicked.connect(self._return_values)
        btn_set_path.clicked.connect(self.change_path)
        btn_hide_database.clicked.connect(self.hide_database)
        btn_show_all_databases.clicked.connect(self.show_all_databases)
        
        ### Organize objects via widgets
        self.data_frame = QFrame()
        self.data_frame.setLayout(QVBoxLayout())
        
        self.setStyleSheet(" .QFrame {border-width: 1; border-radius: 3; border-style: solid; border-color: rgb(10, 10, 10)}")
        """self.data_frame.setStyleSheet("border-width: 1;"
                                   "border-radius: 3;"
                                   "border-style: solid;"
                                   "border-color: rgb(10, 10, 10);"
                                   )"""
        
        self.data_frame.layout().addWidget(self.label_database)
        
        self.buttons_widget = QWidget()
        self.buttons_widget.setLayout(QHBoxLayout())
        self.buttons_widget.layout().addWidget(btn_add_database)
        self.buttons_widget.layout().addWidget(btn_hide_database)
        self.buttons_widget.layout().addWidget(btn_set_path)
        self.buttons_widget.layout().addWidget(btn_show_all_databases)
        self.buttons_widget.layout().addWidget(btn_confirm)
        
        self.data_frame.layout().addWidget(self.buttons_widget)
        
        self.layout().addWidget(self.data_frame)
        self._read_database_files()
        
    def _read_database_files(self):
        """
        Reads database files, re-displays all databases for selection
        """
        data_frame = self.data_frame
        new_data_frame = QFrame()
        new_data_frame.setLayout(QVBoxLayout())
        self.setStyleSheet(" .QFrame {border-width: 1; border-radius: 3; border-style: solid; border-color: rgb(10, 10, 10)}")
        """new_data_frame.setStyleSheet("border-width: 1;"
                                   "border-radius: 3;"
                                   "border-style: solid;"
                                   "border-color: rgb(10, 10, 10);"
                                   )"""
        new_data_frame.layout().addWidget(self.label_database)
        with open(self.hidden_databases_conf_file) as f:
            self.hidden_databases = f.readlines()
        
        self.checkboxes = []
        for file in os.listdir(self.db_directory):
            if not file.endswith(".csv"):
                continue
            print(f"found {file}")
            if f"{file}\n" in self.hidden_databases:
                print(f"skipping {file}")
                continue
            checkbox = QCheckBox(os.path.splitext(file)[0])
            self.checkboxes.append(checkbox)
            new_data_frame.layout().addWidget(checkbox)
            
        new_data_frame.layout().addWidget(self.buttons_widget)
        self.layout().replaceWidget(self.data_frame, new_data_frame)
        self.data_frame.hide()
        self.data_frame = new_data_frame
        
        
    def _add_database(self):
        """
        Adds a template database
        """
        create_new_database(self.db_directory)
        self._read_database_files()
        
    def hide_database(self):
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                write_file(self.hidden_databases_conf_file, f"{checkbox.text()}.csv", True)
        self._read_database_files()
    
    def change_path(self):
        path = f"{select_directory(self)}/"
        if path == "/":
            return
        self.db_directory = path
        write_file(self.config_file, path, newline=False)
        self._read_database_files()
    
    def show_all_databases(self):
        write_file(self.hidden_databases_conf_file, "")
        self._read_database_files()
    
    def _return_values(self):
        """
        Reads data from selected databases, sets data in parent widget and triggers update
        """
        metabolites = {}
        key_list = []
        data = self.layout().itemAt(0).widget().layout()
        for i in range(1, data.indexOf(self.buttons_widget)):
            if data.itemAt(i).widget().isChecked():
                with open(self.db_directory+data.itemAt(i).widget().text() + ".csv", newline='') as csvfile:
                    database_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                    for row in database_reader:
                        metabolites[row[0]] = (row[1],row[2])
                        key_list.append(row[0])

        key_list = sorted(key_list, key = float)
        metabolites_sorted = {key: metabolites[key] for key in key_list}
        self.parent.metabolites = metabolites_sorted
        self.parent.modified_metabolites = self.parent.metabolites
        self.parent.update_mzs()
        self.close()
        
        
        
        