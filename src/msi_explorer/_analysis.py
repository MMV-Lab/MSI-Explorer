from qtpy.QtWidgets import QWidget, QPushButton, QGridLayout, QMessageBox

class AnalysisWindow(QWidget):
    """
    A (QWidget) window to run analysis on selected data
    
    
    Methods
    -------
    function()
        Temporary placeholder function
    """
    def __init__(self):
        super().__init__()
        self.setLayout(QGridLayout())
        
        ### QObjects
        
        # Buttons
        btn_function_1 = QPushButton("Function 1")
        btn_function_2 = QPushButton("Function 2")
        btn_function_3 = QPushButton("Function 3")
        btn_function_4 = QPushButton("Function 4")
        btn_function_5 = QPushButton("Function 5")
        
        btn_function_1.clicked.connect(self._function)
        btn_function_2.clicked.connect(self._function)
        btn_function_3.clicked.connect(self._function)
        btn_function_4.clicked.connect(self._function)
        btn_function_5.clicked.connect(self._function)
        
        ### Organize objects into layout
        
        self.layout().addWidget(btn_function_1,0,0)
        self.layout().addWidget(btn_function_2,0,1)
        self.layout().addWidget(btn_function_3,1,0)
        self.layout().addWidget(btn_function_4,1,1)
        self.layout().addWidget(btn_function_5,2,0)
        
    def _function(self):
        """
        Temporary placeholder function
        """
        msg = QMessageBox()
        msg.setWindowTitle("Hooray!")
        msg.setText("A function")
        msg.setDetailedText("You ran a function.")
        msg.setInformativeText("This function now does stuff!")
        msg.exec()