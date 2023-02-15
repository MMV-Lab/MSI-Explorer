from typing import TYPE_CHECKING

from qtpy.QtWidgets import (QHBoxLayout, QPushButton, QWidget, QComboBox, QLabel, QVBoxLayout,
                            QScrollArea, QLineEdit, QFrame)
from qtpy.QtCore import Qt, QRect

if TYPE_CHECKING:
    import napari
    
from ._selection import SelectionWindow
from ._metadata import MetadataWindow
from ._reader import open_dialog, napari_get_reader
from ._analysis import AnalysisWindow

# TODO: check tests
class ExampleQWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        ### QObjects
        
        # Labels
        label_preprocessing = QLabel('Preprocessing')
        label_scale = QLabel('Scale:')
        label_correction = QLabel('Mass calibration:')
        label_correction_tooltip = 'recalibration/baseline correction'
        label_correction.setToolTip(label_correction_tooltip)
        label_noise_reduction = QLabel('noise reduction:')
        label_roi = QLabel('ROI')

        # Buttons
        btn_load_imzml = QPushButton('Load imzML')
        btn_view_metadata = QPushButton('View Metadata')
        btn_execute_preprocessing = QPushButton('Execute')
        btn_analyze_roi = QPushButton('Analyze')
        btn_minimize_preprocessing = QPushButton('-')
        
        btn_view_metadata.clicked.connect(self._open_metadata)
        btn_load_imzml.clicked.connect(self._open_file)
        btn_analyze_roi.clicked.connect(self._analyze)
        
        # Comboboxes
        combobox_scale = QComboBox()
        combobox_scale.addItems(['original', 'normalized'])
        combobox_roi = QComboBox()
        
        
        # Lineedits
        lineedit_correction = QLineEdit()
        lineedit_noise_reduction = QLineEdit()
        
        ### Variables
        preprocessing_minimized = False

        ### Organize objects via widgets
        # widget: parent widget of all content
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        
        top_buttons = QWidget()
        top_buttons.setLayout(QHBoxLayout())
        top_buttons.layout().addWidget(btn_load_imzml)
        top_buttons.layout().addWidget(btn_view_metadata)
        
        widget.layout().addWidget(top_buttons)
        
        preprocessing_frame = QFrame()
        preprocessing_frame.setLayout(QVBoxLayout())
        
        preprocessing_frame.setStyleSheet("border-width: 1;"
                                   "border-radius: 3;"
                                   "border-style: solid;"
                                   "border-color: rgb(10, 10, 10);"
                                   )
        
        preprocessing_header = QWidget()
        preprocessing_header.setLayout(QHBoxLayout())
        preprocessing_header.layout().addWidget(label_preprocessing)
        preprocessing_header.layout().addWidget(btn_minimize_preprocessing)
        preprocessing_header.layout().setAlignment(btn_minimize_preprocessing,Qt.AlignRight)
        
        preprocessing_frame.layout().addWidget(preprocessing_header)
        
        preprocessing_scale = QWidget()
        preprocessing_scale.setLayout(QHBoxLayout())
        preprocessing_scale.layout().addWidget(label_scale)
        preprocessing_scale.layout().addWidget(combobox_scale)
        
        preprocessing_frame.layout().addWidget(preprocessing_scale)
        
        preprocessing_correction = QWidget()
        preprocessing_correction.setLayout(QHBoxLayout())
        preprocessing_correction.layout().addWidget(label_correction)
        preprocessing_correction.layout().addWidget(lineedit_correction)
        
        preprocessing_frame.layout().addWidget(preprocessing_correction)
        
        preprocessing_noise_reduction = QWidget()
        preprocessing_noise_reduction.setLayout(QHBoxLayout())
        preprocessing_noise_reduction.layout().addWidget(label_noise_reduction)
        preprocessing_noise_reduction.layout().addWidget(lineedit_noise_reduction)
        
        preprocessing_frame.layout().addWidget(preprocessing_noise_reduction)
        
        preprocessing_frame.layout().addWidget(btn_execute_preprocessing)
        
        widget.layout().addWidget(preprocessing_frame)
        
        roi_frame = QFrame()
        roi_frame.setLayout(QVBoxLayout())
        
        roi_frame.setStyleSheet("border-width: 1;"
                                   "border-radius: 3;"
                                   "border-style: solid;"
                                   "border-color: rgb(10, 10, 10);"
                                   )
        roi_frame.layout().addWidget(label_roi)
        
        roi_selection = QWidget()
        roi_selection.setLayout(QHBoxLayout())
        roi_selection.layout().addWidget(combobox_roi)
        roi_selection.layout().addWidget(btn_analyze_roi)
        
        roi_frame.layout().addWidget(roi_selection)
        
        widget.layout().addWidget(roi_frame)
        
        # Scrollarea allows content to be larger than assigned space (small monitor)
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        self.setMinimumSize(400,500) # TODO: find permanent values
        scroll_area.setWidgetResizable(True)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)
        
        ### Create & float selection widget
        self.selection_window = SelectionWindow(self.viewer)
        self.selection_window.show()
        
    def _open_metadata(self):
        self.metadata_window = MetadataWindow()
        self.metadata_window.show()
        
    def _open_file(self):
        filepath = open_dialog(self, '*.imzML')
        file_reader = napari_get_reader(filepath)
        self.ms_object = file_reader(filepath)
        self.selection_window.set_ms_data(self.ms_object)
        self.selection_window.update_plot(self.selection_window.plot(self.ms_object.get_spectrum(34567)))
        self.selection_window.calculate_image(float(self.selection_window.combobox_mz.currentText()))

    def _analyze(self):
        self.analysis_window = AnalysisWindow()
        self.analysis_window.show()
        
        
        