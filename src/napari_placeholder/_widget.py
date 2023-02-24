from typing import TYPE_CHECKING

from qtpy.QtWidgets import (QHBoxLayout, QPushButton, QWidget, QComboBox, QLabel, QVBoxLayout,
                            QScrollArea, QLineEdit, QFrame)
from qtpy.QtCore import Qt

if TYPE_CHECKING:
    import napari
    
from ._selection import SelectionWindow
from ._metadata import MetadataWindow
from ._reader import open_dialog, napari_get_reader
from ._analysis import AnalysisWindow

# TODO: check tests
class ExampleQWidget(QWidget):
    """
    The main widget of our application
    
    Attributes
    ----------
    viewer : Viewer
        The Napari viewer instance
    selection_window : QWidget 
        The window handling the selection of m/z values
    metadata_window : QWidget
        The window handling the exporting of metadata
    ms_object : Maldi_MS
        Maldi_MS object holding the metadata
    analysis_window : QWidget
        The window handling the analysis of selected regions of interest
        
    Methods
    -------
    open_metadata()
        Opens a [MetadataWindow]
    open_file()
        Opens dialog for user to choose a file, passes data to selection_window
    analyze()
        Opens an [AnalysisWindow]
    """
    def __init__(self, napari_viewer):
        """
        Parameters
        ----------
        viewer : Viewer
            The Napari viewer instance
        """
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
        self.btn_maximize_preprocessing = QPushButton('+')
        
        btn_view_metadata.clicked.connect(self._open_metadata)
        btn_load_imzml.clicked.connect(self._open_file)
        btn_analyze_roi.clicked.connect(self._analyze)
        btn_minimize_preprocessing.clicked.connect(self._hide_preprocessing)
        self.btn_maximize_preprocessing.clicked.connect(self._show_preprocessing)
        
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
        widget.layout().addWidget(self.btn_maximize_preprocessing)
        widget.layout().setAlignment(self.btn_maximize_preprocessing,Qt.AlignRight)
        self.btn_maximize_preprocessing.hide()
        
        self.preprocessing_frame = QFrame()
        self.preprocessing_frame.setLayout(QVBoxLayout())
        
        self.preprocessing_frame.setStyleSheet("border-width: 1;"
                                   "border-radius: 3;"
                                   "border-style: solid;"
                                   "border-color: rgb(10, 10, 10);"
                                   )
        
        preprocessing_header = QWidget()
        preprocessing_header.setLayout(QHBoxLayout())
        preprocessing_header.layout().addWidget(label_preprocessing)
        preprocessing_header.layout().addWidget(btn_minimize_preprocessing)
        preprocessing_header.layout().setAlignment(btn_minimize_preprocessing,Qt.AlignRight)
        
        self.preprocessing_frame.layout().addWidget(preprocessing_header)
        
        preprocessing_scale = QWidget()
        preprocessing_scale.setLayout(QHBoxLayout())
        preprocessing_scale.layout().addWidget(label_scale)
        preprocessing_scale.layout().addWidget(combobox_scale)
        
        self.preprocessing_frame.layout().addWidget(preprocessing_scale)
        
        preprocessing_correction = QWidget()
        preprocessing_correction.setLayout(QHBoxLayout())
        preprocessing_correction.layout().addWidget(label_correction)
        preprocessing_correction.layout().addWidget(lineedit_correction)
        
        self.preprocessing_frame.layout().addWidget(preprocessing_correction)
        
        preprocessing_noise_reduction = QWidget()
        preprocessing_noise_reduction.setLayout(QHBoxLayout())
        preprocessing_noise_reduction.layout().addWidget(label_noise_reduction)
        preprocessing_noise_reduction.layout().addWidget(lineedit_noise_reduction)
        
        self.preprocessing_frame.layout().addWidget(preprocessing_noise_reduction)
        
        self.preprocessing_frame.layout().addWidget(btn_execute_preprocessing)
        
        widget.layout().addWidget(self.preprocessing_frame)
        
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
        
    # opens metadata window
    def _open_metadata(self):
        """
        Opens a [MetadataWindow]
        """
        self.metadata_window = MetadataWindow()
        self.metadata_window.show()
        
    # opens imzml file
    def _open_file(self):
        """
        Opens dialog for user to choose a file, passes data to selection_window
        """
        filepath = open_dialog(self, '*.imzML')
        file_reader = napari_get_reader(filepath)
        try:
            self.ms_object = file_reader(filepath)
        except TypeError:
            return
        self.selection_window.set_data(self.ms_object, self.ms_object.get_spectrum(34567))
        self.selection_window.update_plot(self.selection_window.data_array)
        try:
            self.selection_window.calculate_image(float(self.selection_window.combobox_mz.currentText()))
        except ValueError:
            pass
        else:
            self.selection_window.display_description(float(self.selection_window.combobox_mz.currentText()))

    # opens analysis window
    def _analyze(self):
        """
        Opens an [AnalysisWindow]
        """
        self.analysis_window = AnalysisWindow()
        self.analysis_window.show()
        
        
    # hides preprocessing steps
    def _hide_preprocessing(self):
        self.btn_maximize_preprocessing.show()
        self.preprocessing_frame.hide()
        
        
    # shows preprocessing steps
    def _show_preprocessing(self):
        self.preprocessing_frame.show()
        self.btn_maximize_preprocessing.hide()
        
        
        
