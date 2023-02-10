from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton,
                            QComboBox, QLineEdit)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from ._database import DatabaseWindow

class SelectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.canvas = self.plot()
        self.mzs = []
        ### QObjects
        
        # Labels
        label_select_database = QLabel("Select database")
        label_mz = QLabel("m/z")
        label_range = QLabel("Range:")
        label_mode = QLabel("Mode")
        label_mz_annotation = QLabel("")
        
        # Buttons
        btn_reset_view = QPushButton("Reset")
        btn_display_current_view = QPushButton("Show image")
        btn_select_database = QPushButton("Select")
        
        btn_select_database.clicked.connect(self.select_database)
        
        # Radiobuttons
        radio_btn_replace_layer = QRadioButton("Single panel_view")
        radio_btn_add_layer = QRadioButton("Multi")
        radio_btn_replace_layer.toggle()
        
        # Lineedits
        lineedit_mz_range = QLineEdit()
        
        # Comboboxes
        combobox_mz = QComboBox()
        
        ### Organize objects via widgets
        visual_frame = QWidget()
        visual_frame.setLayout(QHBoxLayout())  
        visual_frame.layout().addWidget(self.canvas)
        
        visual_buttons = QWidget()
        visual_buttons.setLayout(QVBoxLayout())
        visual_buttons.layout().addWidget(btn_reset_view)
        visual_buttons.layout().addWidget(btn_display_current_view)
        
        visual_frame.layout().addWidget(visual_buttons)
        
        self.layout().addWidget(visual_frame)
        
        database_frame = QWidget()
        database_frame.setLayout(QHBoxLayout())
        database_frame.layout().addWidget(label_select_database)
        database_frame.layout().addWidget(btn_select_database)
        
        self.layout().addWidget(database_frame)
        
        mz_frame = QWidget()
        mz_frame.setLayout(QHBoxLayout())
        mz_frame.layout().addWidget(label_mz)
        mz_frame.layout().addWidget(combobox_mz)
        mz_frame.layout().addWidget(label_mz_annotation)
        mz_frame.layout().addWidget(label_range)
        mz_frame.layout().addWidget(lineedit_mz_range)
        
        self.layout().addWidget(mz_frame)
        
        display_mode_frame = QWidget()
        display_mode_frame.setLayout(QHBoxLayout())
        display_mode_frame.layout().addWidget(label_mode)
        display_mode_frame.layout().addWidget(radio_btn_replace_layer)
        display_mode_frame.layout().addWidget(radio_btn_add_layer)
        
        self.layout().addWidget(display_mode_frame)
        
    def plot(self, data = None):
        fig = Figure(figsize=(6,6))
        #fig.patch.set_facecolor("#262930")
        axes = fig.add_subplot(111)
        #axes.set_facecolor("#262930")
        """axes.spines["bottom"].set_color("white")
        axes.spines["top"].set_color("white")
        axes.spines["right"].set_color("white")
        axes.spines["left"].set_color("white")
        axes.xaxis.label.set_color("white")
        axes.yaxis.label.set_color("white")"""
        axes.tick_params(axis="x")
        axes.tick_params(axis="y")
        """axes.tick_params(axis="x", colors="white")
        axes.tick_params(axis="y", colors="white")"""
        if data is None:
            axes.plot()
        else:
            axes.plot(data[0],data[1])
        return FigureCanvas(fig)
    
    def update_plot(self, new_canvas):
        old_canvas = self.canvas
        self.layout().itemAt(0).widget().layout().removeWidget(old_canvas)
        old_canvas.hide()
        self.layout().itemAt(0).widget().layout().insertWidget(0,new_canvas)
        self.canvas = new_canvas
        
    def select_database(self):
        self.database_window = DatabaseWindow(self)
        self.database_window.show()
        