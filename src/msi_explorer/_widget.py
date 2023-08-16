from typing import TYPE_CHECKING

from qtpy.QtWidgets import (QHBoxLayout, QPushButton, QWidget, QComboBox, QLabel, QVBoxLayout,
                            QScrollArea, QLineEdit, QFrame, QMessageBox, QApplication, QGridLayout)
from qtpy.QtCore import Qt

if TYPE_CHECKING:
    import napari
    
from ._selection import SelectionWindow
from ._metadata import MetadataWindow
from ._reader import open_dialog, napari_get_reader
from ._analysis import AnalysisWindow

# TODO: check tests
class MSI_Explorer(QWidget):
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
        self.label_reference = QLabel('reference:')

        # Buttons
        btn_load_imzml = QPushButton('Load imzML')
        self.btn_view_metadata = QPushButton('View Metadata')
        self.btn_execute_preprocessing = QPushButton('Execute')
        self.btn_analyze_roi = QPushButton('Analyze')
        btn_minimize_preprocessing = QPushButton('-')
        self.btn_maximize_preprocessing = QPushButton('+')
        
        self.btn_view_metadata.clicked.connect(self._open_metadata)
        btn_load_imzml.clicked.connect(self._open_file)
        self.btn_analyze_roi.clicked.connect(self._analyze)
        self.btn_execute_preprocessing.clicked.connect(self.preprocess)
        btn_minimize_preprocessing.clicked.connect(self._hide_preprocessing)
        self.btn_maximize_preprocessing.clicked.connect(self._show_preprocessing)
        
        self.btn_view_metadata.setEnabled(False)
        self.btn_execute_preprocessing.setEnabled(False)
        self.btn_analyze_roi.setEnabled(False)
        
        # Comboboxes
        self.combobox_scale = QComboBox()
        self.combobox_scale.addItems(['original', 'tic','rms','median', 'peak'])
        self.combobox_scale.currentTextChanged.connect(self.toggle_reference_selection)
        combobox_roi = QComboBox()
        
        
        # Lineedits
        lineedit_correction = QLineEdit()
        lineedit_noise_reduction = QLineEdit()
        self.lineedit_reference = QLineEdit()
        self.lineedit_reference.setPlaceholderText("M/Z")
        self.lineedit_reference.hide()
        self.label_reference.hide()
        
        ### Variables
        preprocessing_minimized = False

        ### Organize objects via widgets
        # widget: parent widget of all content
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        
        top_buttons = QWidget()
        top_buttons.setLayout(QHBoxLayout())
        top_buttons.layout().addWidget(btn_load_imzml)
        top_buttons.layout().addWidget(self.btn_view_metadata)
        
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
        preprocessing_scale.setLayout(QGridLayout())
        preprocessing_scale.layout().addWidget(label_scale,0,0)
        preprocessing_scale.layout().addWidget(self.combobox_scale,0,1)
        preprocessing_scale.layout().addWidget(self.label_reference,1,0)
        preprocessing_scale.layout().addWidget(self.lineedit_reference,1,1)
        
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
        
        self.preprocessing_frame.layout().addWidget(self.btn_execute_preprocessing)
        
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
        roi_selection.layout().addWidget(self.btn_analyze_roi)
        
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
        if not hasattr(self,"ms_object"):
            return
        self.metadata_window = MetadataWindow(self.ms_object, self)
        self.metadata_window.show()
        
    # opens imzml file
    def _open_file(self):
        """
        Opens dialog for user to choose a file, passes data to selection_window
        """
        filepath = open_dialog(self, '*.imzML')
        QApplication.setOverrideCursor(Qt.WaitCursor)
        file_reader = napari_get_reader(filepath)
        import warnings
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.ms_object = file_reader(filepath)
        except TypeError:
            QApplication.restoreOverrideCursor()
            return
        except UnboundLocalError:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(".ibd file not found in same directory")
            QApplication.restoreOverrideCursor()
            msg.exec()
            return
        
        # Take spectrum from the center as a default spectrum
        x = int(self.ms_object.get_metadata()['max count x'] / 2)
        y = int(self.ms_object.get_metadata()['max count y'] / 2)
        index = self.ms_object.get_index(y, x)
        title = "Original {}, #{}".format((x,y), index)
        self.selection_window.set_data(self.ms_object, self.ms_object.get_spectrum(index))
        self.selection_window.plot_spectrum(title = title)
        #self.selection_window.update_plot(self.selection_window.data_array, position = position)
        self.selection_window.display_image_from_plot()
        
        # enable buttons after loading data
        self.btn_view_metadata.setEnabled(True)
        self.btn_execute_preprocessing.setEnabled(True)
        self.btn_analyze_roi.setEnabled(True)
        self.selection_window.btn_reset_view.setEnabled(True)
        self.selection_window.btn_display_current_view.setEnabled(True)
        #self.selection_window.btn_pseudo_mean_spectrum.setEnabled(True)
        self.selection_window.btn_select_roi.setEnabled(True)
        self.selection_window.btn_true_mean_spectrum.setEnabled(True)
        self.selection_window.btn_export_spectrum_data.setEnabled(True)
        self.selection_window.btn_export_spectrum_plot.setEnabled(True)
        QApplication.restoreOverrideCursor()
        
    def preprocess(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        normalization_method = self.combobox_scale.currentText()
        if self.lineedit_reference.text() != '':
            mz = float(self.lineedit_reference.text())
            self.ms_object.normalize(normalization_method, mz)
        else:
            self.ms_object.normalize(normalization_method)
        QApplication.restoreOverrideCursor()

    def _analyze(self):
        """
        Opens an [AnalysisWindow]
        """
        self.analysis_window = AnalysisWindow()
        self.analysis_window.show()
        
    def _hide_preprocessing(self):
        """
        Hides preprocessing steps
        """
        self.btn_maximize_preprocessing.show()
        self.preprocessing_frame.hide()
        
    def _show_preprocessing(self):
        """
        Shows preprocessing steps
        """
        self.preprocessing_frame.show()
        self.btn_maximize_preprocessing.hide()
        
    def toggle_reference_selection(self, metric):
        if metric == 'peak':
            self.label_reference.show()
            self.lineedit_reference.show()
        else:
            self.label_reference.hide()
            self.lineedit_reference.hide()
        
        
        
