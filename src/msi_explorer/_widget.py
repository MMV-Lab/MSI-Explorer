# from typing import TYPE_CHECKING
import warnings
import os

from qtpy.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QWidget,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QScrollArea,
    QLineEdit,
    QMessageBox,
    QApplication,
    QGridLayout,
    QGroupBox,
    QCheckBox,
)
from qtpy.QtCore import Qt
from qtpy.QtGui import QImage, QPixmap
import cv2

from ._selection import SelectionWindow
from ._metadata import MetadataWindow
from ._reader import open_dialog, napari_get_reader
from ._analysis import AnalysisWindow

# if TYPE_CHECKING:
#     import napari


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
        
        # Logo
        filename = "logo.png"
        absolute_path = os.path.dirname(os.path.abspath(__file__))
        relative_path = os.path.join("ressources/",filename)
        path = os.path.join(absolute_path,relative_path)
        image = cv2.imread(path)
        rescaled_image = cv2.resize(image, (300, 300))
        height, width, _ = rescaled_image.shape
        logo = QPixmap(QImage(rescaled_image.data, width, height, 3* width, QImage.Format_BGR888))

        # Labels
        label_title = QLabel()
        label_title.setPixmap(logo)
        label_title.setAlignment(Qt.AlignCenter)
        label_scale = QLabel("Normalization:")
        label_noise_reduction = QLabel("Noise reduction:")
        label_hotspot_removal = QLabel("Hotspot removal:")
        self.label_reference = QLabel("Reference:")

        # Buttons
        btn_load_imzml = QPushButton("Load imzML")
        btn_load_imzml.setStyleSheet('''
                                     QPushButton {
                                         font-size: 20px;
                                     }
                                ''')
        self.btn_view_metadata = QPushButton("View Metadata")
        self.btn_execute_preprocessing = QPushButton("Execute")
        self.btn_analyze_roi = QPushButton("Analyze")
        btn_minimize_preprocessing = QPushButton("-")
        self.btn_maximize_preprocessing = QPushButton("+")

        self.btn_view_metadata.clicked.connect(self.open_metadata)
        btn_load_imzml.clicked.connect(self._open_file)
        self.btn_analyze_roi.clicked.connect(self._analyze)
        self.btn_execute_preprocessing.clicked.connect(self.preprocess)
        btn_minimize_preprocessing.clicked.connect(self._hide_preprocessing)
        self.btn_maximize_preprocessing.clicked.connect(
            self._show_preprocessing
        )

        self.btn_view_metadata.setEnabled(False)
        self.btn_execute_preprocessing.setEnabled(False)
        self.btn_analyze_roi.setEnabled(False)

        # Comboboxes
        self.combobox_scale = QComboBox()
        self.combobox_scale.addItems(
            ["original", "tic", "rms", "median", "peak"]
        )
        self.combobox_scale.currentTextChanged.connect(
            self.toggle_reference_selection
        )
        combobox_roi = QComboBox()

        # Lineedits
        self.lineedit_noise_reduction = QLineEdit()
        self.lineedit_noise_reduction.setText("0.01")
        self.lineedit_hotspot_removal = QLineEdit()
        self.lineedit_hotspot_removal.setText("99.99")
        self.lineedit_reference = QLineEdit()
        self.lineedit_reference.setPlaceholderText("M/Z")
        self.lineedit_reference.hide()
        self.label_reference.hide()

        # QCheckBox
        self.checkbox_noise_reduction = QCheckBox("")
        self.checkbox_hotspot_removal = QCheckBox("")

        # Groupboxes
        self.groupbox_preprocessing = QGroupBox()
        self.groupbox_preprocessing.setTitle("Preprocessing")
        preprocessing_layout = QGridLayout()
        preprocessing_layout.addWidget(btn_minimize_preprocessing, 0, 3)
        preprocessing_layout.addWidget(label_noise_reduction, 1, 0, 1, 1)
        preprocessing_layout.addWidget(self.lineedit_noise_reduction, 1, 1, 1, 2)
        preprocessing_layout.addWidget(self.checkbox_noise_reduction, 1, 3, 1, 1)
        preprocessing_layout.addWidget(label_scale, 2, 0, 1, 1)
        preprocessing_layout.addWidget(self.combobox_scale, 2, 1, 1, 2)
        preprocessing_layout.addWidget(label_hotspot_removal, 3, 0, 1, 1)
        preprocessing_layout.addWidget(self.lineedit_hotspot_removal, 3, 1, 1, 2)
        preprocessing_layout.addWidget(self.checkbox_hotspot_removal, 3, 3, 1, 1)
        preprocessing_layout.addWidget(self.btn_execute_preprocessing, 10, 1, 1, 1)
        
        self.groupbox_preprocessing.setLayout(preprocessing_layout)
        self.groupbox_roi = QGroupBox()
        self.groupbox_roi.setTitle("ROI")
        self.groupbox_roi.setLayout(QHBoxLayout())
        self.groupbox_roi.layout().addWidget(combobox_roi)
        self.groupbox_roi.layout().addWidget(self.btn_analyze_roi)

        ### Organize objects via widgets
        # widget: parent widget of all content
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        
        widget.layout().addWidget(label_title)

        top_buttons = QWidget()
        top_buttons.setLayout(QHBoxLayout())
        top_buttons.layout().addWidget(btn_load_imzml)
        top_buttons.layout().addWidget(self.btn_view_metadata)

        widget.layout().addWidget(top_buttons)
        widget.layout().addWidget(self.btn_maximize_preprocessing)
        widget.layout().setAlignment(
            self.btn_maximize_preprocessing, Qt.AlignRight
        )
        self.btn_maximize_preprocessing.hide()

        widget.layout().addWidget(self.groupbox_preprocessing)
        widget.layout().addWidget(self.groupbox_roi)

        # Scrollarea allows content to be larger than assigned space (small monitor)
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        self.setMinimumSize(400, 500)
        scroll_area.setWidgetResizable(True)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)

        ### Create & float selection widget
        self.selection_window = SelectionWindow(self)
        self.selection_window.show()

    # opens metadata window
    def open_metadata(self):
        """
        Opens a [MetadataWindow]
        """
        if not hasattr(self, "ms_object"):
            return
        self.metadata_window = MetadataWindow(self.ms_object, self)
        self.metadata_window.show()

    # opens imzml file
    def _open_file(self):
        """
        Opens dialog for user to choose a file, passes data to selection_window
        """
        filepath = open_dialog(self, "*.imzML *.imzml")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        file_reader = napari_get_reader(filepath)

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
        
        # check if data is in centroid mode
        if not self.ms_object.check_centroid():
            QApplication.restoreOverrideCursor()
            msg = QMessageBox()
            msg.setWindowTitle("Profile detected")
            msg.setText("It appears the data is stored in profile mode. " + \
            "Do you want to convert it to centroid mode now?")
            msg.addButton(QMessageBox.Yes)
            msg.addButton(QMessageBox.No)
            if msg.exec() == 16384:
                self.ms_object.centroid_data()
                
            #16384 for yes, 65536 for no
            

        # Take spectrum from the center as a default spectrum
        x = int(self.ms_object.get_metadata()["max count x"] / 2)
        y = int(self.ms_object.get_metadata()["max count y"] / 2)
        index = self.ms_object.get_index(y, x)
        title = f"Original {(x,y)}, #{index}"
        self.selection_window.set_data(
            self.ms_object, self.ms_object.get_spectrum(index)
        )
        self.selection_window.plot_spectrum(title=title)
        try:
            self.selection_window.display_image_from_plot()
        except RuntimeError:
            msg = QMessageBox()
            msg.setWindowTitle("Metadata Error")
            msg.setText(
                "Metadata is incorrect. Please make sure the max count x and y are correct."
            )
            msg.exec()
            self.ms_object = None
            self.selection_window.reset()
            return
        self.selection_window.mean_spectra.clear()

        # enable buttons after loading data
        self.btn_view_metadata.setEnabled(True)
        self.btn_execute_preprocessing.setEnabled(True)
        self.btn_analyze_roi.setEnabled(True)
        self.selection_window.btn_reset_view.setEnabled(True)
        self.selection_window.btn_display_current_view.setEnabled(True)
        self.selection_window.btn_select_roi.setEnabled(True)
        self.selection_window.btn_true_mean_spectrum.setEnabled(True)
        self.selection_window.btn_export_spectrum_data.setEnabled(True)
        self.selection_window.btn_export_spectrum_plot.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def preprocess(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.checkbox_noise_reduction.isChecked():
            try:
                filter_limit = float(self.lineedit_noise_reduction.text())
            except ValueError:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("Noise reduction value is not a number")
                msg.exec()
                return
            if filter_limit < 0 or filter_limit > 100:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("Noise reduction value must be between 0 and 100")
                msg.exec()
                return
            self.ms_object.noise_reduction(filter_limit)
        normalization_method = self.combobox_scale.currentText()
        if self.lineedit_reference.text() != "":
            mz = float(self.lineedit_reference.text())
            self.ms_object.normalize(normalization_method, mz)
        else:
            self.ms_object.normalize(normalization_method)
        if self.checkbox_hotspot_removal.isChecked():
            try:
                filter_limit = float(self.lineedit_hotspot_removal.text())
            except ValueError:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("Hotspot removal value is not a number")
                msg.exec()
                return
            if filter_limit < 0 or filter_limit > 100:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("Hotspot removal value must be between 0 and 100")
                msg.exec()
                return
            self.ms_object.remove_hotspots(filter_limit)
        QApplication.restoreOverrideCursor()

    def _analyze(self):
        """
        Opens an [AnalysisWindow]
        """
        self.analysis_window = AnalysisWindow(self.viewer)
        self.analysis_window.show()

    def _hide_preprocessing(self):
        """
        Hides preprocessing steps
        """
        self.btn_maximize_preprocessing.show()
        self.groupbox_preprocessing.hide()

    def _show_preprocessing(self):
        """
        Shows preprocessing steps
        """
        self.groupbox_preprocessing.show()
        self.btn_maximize_preprocessing.hide()

    def toggle_reference_selection(self, metric):
        if metric == "peak":
            self.label_reference.show()
            self.lineedit_reference.show()
        else:
            self.label_reference.hide()
            self.lineedit_reference.hide()
