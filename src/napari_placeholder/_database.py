from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QCheckBox, QPushButton
import csv, os

from ._writer import create_new_database
from ._reader import open_dialog

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
        self.db_directory = os.path.dirname(__file__) + "/databases/"
        
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
        """
        Reads database files, re-displays all databases for selection
        """
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
    
    def _delete_database(self):
        """
        Opens a file dialog in the database directory. Deletes selected csv file
        """
        filepath = open_dialog(self, filetype = "*csv", directory = self.db_directory)
        try:
            os.remove(filepath)
        except FileNotFoundError:
            return
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
                    database_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                    for row in database_reader:
                        metabolites[row[0]] = (row[1],row[2])
                        key_list.append(row[0])

        key_list = sorted(key_list, key = float)
        metabolites_sorted = {key: metabolites[key] for key in key_list}
        self.parent.metabolites = metabolites_sorted
        self.parent.update_mzs()
        self.close()
        
        
        
        