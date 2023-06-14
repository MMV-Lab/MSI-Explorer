from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton,
                            QComboBox, QLineEdit, QSizePolicy, QVBoxLayout, QGridLayout)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

from ._database import DatabaseWindow
from ._maldi_ms_data import Maldi_MS
from ._true_mean_spec import get_true_mean_spec
from ._writer import save_dialog

class SelectionWindow(QWidget):
    """
    A (QWidget) window to handle selection of m/z values
    
    Attributes
    ----------
    viewer : Viewer
        The Napari viewer instance
    metabolites : dict
        Holds all information about m/z, (name, description)
    label_mz_annotation : QLabel
        Displays description of m/z
    radio_btn_replace_layer : QRadioButton
        Determines if main image layer is replaced or new one is created
    lineedit_mz_range : QLineEdit
        Tolerance in calculating image from m/z
    lineedit_mz_filter : QLineEdit
        Filter string for metabolites
    combobox_mz : QComboBox
        Holds all selectable m/z values
    database_window : QWidget
        The window to select databases to be used
    ms_object : Maldi_MS
        Maldi_MS object holding the metadata
    data_array : array
        array holding X and Y coordinates of the current spectrum
    displayed_data : array
        array holding X and Y coordinates of the currently displayed part of the current spectrum
    sample_mean_spectrum : tuple
        tuple holding numpy arrays with X and Y coordinates of the mean spectrum
    
    Methods
    -------
    keyPressEvent(event)
        gets spectrum at position of [event] and passes it to [update_plot]
    plot(data)
        Creates a canvas for a given spectrum
    update_plot(data)
        Replaces displayed canvas with new canvas
    reset_plot()
        Replaces canvas with fully zoomed out canvas
    select_database()
        Opens a [DatabaseWindow]
    calculate_image(mz, tolerance)
        Replaces/Adds new image layer with selected m/z & tolerance
    set_data()
        Set MSObject and the current spectrum data as attributes
    update_mzs()
        Updates the m/z values displayed in the combobox to match those selected from the databases
    display_description()
        Adds the description of the metabolite to the label
    filter_mzs()
        Filters metabolites by text in lineedit_mz_filter
    display_image_from_plot()
        Displays image of the currently displayed m/z range in the plot
    sample_mean_spectrum()
        Displays the mean spectrum in the graph view
    """
    def __init__(self, viewer):
        """
        Parameters
        ----------
        viewer : Viewer
            The Napari viewer instance
        """
        super().__init__()
        self.viewer = viewer
        self.setLayout(QVBoxLayout())

        self.plot()
        self.metabolites = {}
        
        ### QObjects
        
        # Labels
        label_mean = QLabel("Mean")
        label_mean.setMaximumWidth(80)
        label_select_database = QLabel("Select database")
        label_select_database.setMaximumWidth(180)
        label_search = QLabel("Search")
        label_search.setMaximumWidth(80)
        label_mz = QLabel("Molecule")
        label_mz.setMaximumWidth(100)
        label_range = QLabel("Range")
        label_range.setMaximumWidth(80)
        label_mode = QLabel("Display Mode")
        label_mode.setMaximumWidth(160)
        
        self.label_mz_annotation = QLabel("Annotation")
        self.label_mz_annotation.setMinimumWidth(200)
        self.label_mz_annotation.setMaximumWidth(600)
        
        # Buttons
        self.btn_reset_view = QPushButton("Reset")
        self.btn_reset_view.setMaximumWidth(80)
        self.btn_display_current_view = QPushButton("Show image")
        self.btn_display_current_view.setMaximumWidth(120)
        self.btn_export_spectrum_data = QPushButton("Export spectrum data")
        self.btn_export_spectrum_data.setMaximumWidth(180)
        self.btn_export_spectrum_plot = QPushButton("Export spectrum plot")
        self.btn_export_spectrum_plot.setMaximumWidth(180)
        btn_select_database = QPushButton("Select")
        btn_select_database.setMaximumWidth(80)
        self.btn_pseudo_mean_spectrum = QPushButton("Show pseudo mean spectrum")
        self.btn_pseudo_mean_spectrum.setMaximumWidth(220)
        self.btn_true_mean_spectrum = QPushButton("Show true mean spectrum")
        self.btn_true_mean_spectrum.setMaximumWidth(200)
        
        self.btn_true_mean_spectrum.setToolTip(
            "WARNING: This will most likely take a while the first time you run it!"
        )
        
        self.btn_reset_view.clicked.connect(self.reset_plot)
        self.btn_display_current_view.clicked.connect(self.display_image_from_plot)
        btn_select_database.clicked.connect(self.select_database)
        self.btn_pseudo_mean_spectrum.clicked.connect(self.sample_mean_spectrum)
        self.btn_true_mean_spectrum.clicked.connect(self.calculate_true_mean_spectrum)
        self.btn_export_spectrum_data.clicked.connect(self.export_spectrum_data)
        self.btn_export_spectrum_plot.clicked.connect(self.export_spectrum_plot)
        
        self.btn_reset_view.setEnabled(False)
        self.btn_display_current_view.setEnabled(False)
        self.btn_pseudo_mean_spectrum.setEnabled(False)
        self.btn_true_mean_spectrum.setEnabled(False)
        self.btn_export_spectrum_data.setEnabled(False)
        self.btn_export_spectrum_plot.setEnabled(False)
        
        # Radiobuttons
        self.radio_btn_replace_layer = QRadioButton("Single panel_view")
        self.radio_btn_replace_layer.setMaximumWidth(180)
        radio_btn_add_layer = QRadioButton("Multi")
        radio_btn_add_layer.setMaximumWidth(80)
        self.radio_btn_replace_layer.toggle()
        
        # Lineedits
        self.lineedit_mz_range = QLineEdit("0.1")
        self.lineedit_mz_range.setMaximumWidth(100)
        self.lineedit_mz_filter = QLineEdit()
        self.lineedit_mz_filter.setMaximumWidth(400)
        self.lineedit_mz_filter.setPlaceholderText("Filter")
        
        self.lineedit_mz_filter.editingFinished.connect(self.filter_mzs)
        
        # Comboboxes
        self.combobox_mz = QComboBox()
        self.combobox_mz.setMinimumWidth(100)
        self.combobox_mz.setMaximumWidth(200)
        
        self.combobox_mz.currentTextChanged.connect(self.calculate_image)
        self.combobox_mz.currentTextChanged.connect(self.display_description)
        
        # Lines
        line_1 = QWidget()
        line_1.setFixedHeight(4)
        line_1.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        line_1.setStyleSheet("background-color: #c0c0c0")
        
        line_2 = QWidget()
        line_2.setFixedHeight(4)
        line_2.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        line_2.setStyleSheet("background-color: #c0c0c0")
        
        line_3 = QWidget()
        line_3.setFixedHeight(4)
        line_3.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        line_3.setStyleSheet("background-color: #c0c0c0")
        
        line_4 = QWidget()
        line_4.setFixedHeight(4)
        line_4.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        line_4.setStyleSheet("background-color: #c0c0c0")
        
        ### Organize objects via widgets
        
        self.layout().addWidget(self.canvas)
        
        visual_buttons = QWidget()
        visual_buttons.setLayout(QHBoxLayout())
        visual_buttons.layout().addWidget(self.btn_display_current_view)
        visual_buttons.layout().addWidget(self.btn_reset_view)
        visual_buttons.layout().addWidget(self.btn_export_spectrum_data)
        visual_buttons.layout().addWidget(self.btn_export_spectrum_plot)
        
        self.layout().addWidget(visual_buttons)
        self.layout().addWidget(line_1)
        
        mean_frame = QWidget()
        mean_frame.setLayout(QHBoxLayout())
        mean_frame.layout().addWidget(label_mean)
        mean_frame.layout().addWidget(self.btn_true_mean_spectrum)
        mean_frame.layout().addWidget(self.btn_pseudo_mean_spectrum)
        
        self.layout().addWidget(mean_frame)
        self.layout().addWidget(line_2)
        
        database_frame = QWidget()
        database_frame.setLayout(QHBoxLayout())
        database_frame.layout().addWidget(label_select_database)
        database_frame.layout().addWidget(btn_select_database)
        
        self.layout().addWidget(database_frame)
        self.layout().addWidget(line_3)
        
        mz_frame = QWidget()
        mz_frame.setLayout(QGridLayout())
        mz_frame.layout().addWidget(label_search, 0, 0)
        mz_frame.layout().addWidget(label_mz,1,0)
        mz_frame.layout().addWidget(self.lineedit_mz_filter,1,1)
        mz_frame.layout().addWidget(self.combobox_mz,2,1)
        mz_frame.layout().addWidget(self.label_mz_annotation,2,2,)
        mz_frame.layout().addWidget(label_range,1,3)
        mz_frame.layout().addWidget(self.lineedit_mz_range,2,3)
        
        self.layout().addWidget(mz_frame)
        self.layout().addWidget(line_4)
        
        display_mode_frame = QWidget()
        display_mode_frame.setLayout(QHBoxLayout())
        display_mode_frame.layout().addWidget(label_mode)
        display_mode_frame.layout().addWidget(self.radio_btn_replace_layer)
        display_mode_frame.layout().addWidget(radio_btn_add_layer)
        
        self.layout().addWidget(display_mode_frame)
        
        @self.viewer.bind_key('s')
        def read_cursor_position(viewer):
            """
            Gets index of spectrum at cursor position,
            gets spectrum at index,
            passes spectrum to [update_plot]
            
            Parameters
            ----------
            viewer : Viewer
                The Napari viewer instance
            """
            index = self.ms_object.get_index(
                round(viewer.cursor.position[0]),round(viewer.cursor.position[1])
            )
            position = "{}, #{}".format((round(viewer.cursor.position[0]),round(viewer.cursor.position[1])),
                                        self.ms_object.get_index(round(viewer.cursor.position[0]), round(viewer.cursor.position[1])))
            if index == -1:
                return
            data = self.ms_object.get_spectrum(index)
            self.update_plot(data, position)
        
    def keyPressEvent(self, event):
        """
        Gets index of spectrum at event position,
        gets spectrum at index,
        passes spectrum to [update_plot]
        
        Parameters
        ----------
        event : Event
            The Event calling this function
        """
        if event.text() == 's':
            index = self.ms_object.get_index(
                round(self.viewer.cursor.position[0]),round(self.viewer.cursor.position[1])
            )
            position = "{}, #{}".format((round(self.viewer.cursor.position[0]),round(self.viewer.cursor.position[1])),
                                        self.ms_object.get_index(round(self.viewer.cursor.position[0]), round(self.viewer.cursor.position[1])))
            if index == -1:
                return
            data = self.ms_object.get_spectrum(index)
            self.update_plot(data, position)
        
    # creates plot from passed data
    def plot(self, data = None, position = None):
        """
        Creates a canvas for a given spectrum [data]
        
        If the argument `data` is not passed in, an empty canvas is produced
        
        Parameters
        ----------
        data : list, optional
            The numpy arrays holding x and y coordinates (default is None)
        position : tupple, optional
            Position of the selected spectrum
            
        Returns
        -------
        canvas
            A canvas displaying the passed spectrum
        """
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
        axes.set_xlabel("m/z")
        axes.set_ylabel("intensity")
        """axes.tick_params(axis="x", colors="white")
        axes.tick_params(axis="y", colors="white")"""
        
        
        if data is None:
            axes.plot()
        else:
            axes.plot(data[0],data[1])
            axes.set_title(position)
            
        canvas = FigureCanvas(fig)
            
        def onselect(min, max):
            """
            Triggers update of plot to display only data between min and max
            
            Parameters
            ----------
            min : int
                Minimum m/z value to be displayed
            max : int
                Maximum m/z value to be displayed
            """
            if not hasattr(self, 'data_array'):
                return
                
            min_bound = self.data_array[:,self.data_array[0,:] >= min]
            both_bound = min_bound[:,min_bound[0,:] <= max]
            self.update_plot(both_bound)
    
        from matplotlib.widgets import SpanSelector
        self.selector = SpanSelector(axes, onselect = onselect, direction = "horizontal")
        self.canvas = canvas
        return canvas
    
    def update_plot(self, data, position = None):
        """
        Replaces displayed canvas with new canvas created from [data]
        
        Parameters
        ----------
        data : list
            The numpy arrays holding x and y coordinates
        position : tuple, optional
            Position of the selected spectrum
        """
        self.displayed_data = np.array(data)
        old_canvas = self.canvas
        new_canvas = self.plot(data, position)
        self.layout().replaceWidget(old_canvas, new_canvas)
        #self.layout().itemAt(0).widget().layout().removeWidget(old_canvas)
        old_canvas.hide()
        #self.layout().itemAt(0).widget().layout().insertWidget(0,new_canvas)
        
    def reset_plot(self):
        """
        Replaces canvas with fully zoomed out canvas
        """
        self.update_plot(self.data_array)
        
    def select_database(self):
        """
        Opens a [DatabaseWindow]
        """
        self.database_window = DatabaseWindow(self)
        self.database_window.show()
        
    def calculate_image(self, mz, tolerance = None):
        """
        Replaces/Adds new image layer with selected m/z & tolerance
        
        Parameters
        ----------
        mz : str
            the m/z value to calculate the image for
        tolerance : float
            the tolerance for the m/z value
        """
        if mz == '':
            return
        mz = float(mz)
        if tolerance == None:
            tolerance = float(self.lineedit_mz_range.text())
        try:
            image = self.ms_object.get_ion_image(mz, tolerance)
        except AttributeError:
            return
        if self.radio_btn_replace_layer.isChecked():
            try:
                self.viewer.layers.remove("main view")
            except ValueError:
                pass
            self.viewer.add_image(image, name = "main view", colormap = "inferno")
        else:
            layername = "m/z " + str(round(mz - tolerance,3)) + " - " + str(mz + tolerance)
            self.viewer.add_image(image, name = layername, colormap = "inferno")
    
    # Sets MAldiMsData object
    def set_data(self, ms_data, data):
        """
        Set MSObject and the current spectrum data as attributes. Writes mean spectrum
        
        Parameters
        ----------
        ms_data : Maldi_MS
            Maldi_MS object holding the metadata of the loaded imzML file
        data : list
            Arrays of X/Y coordinates of spectrum
        """
        self.ms_object = ms_data
        self.data_array = np.array(data)
        self.displayed_data = self.data_array
        self.sample_mean_spectrum = self.ms_object.pseudo_mean_spec() # TODO: put in separate thread
        
    def update_mzs(self):
        """
        Updates the m/z values displayed in the combobox to match those selected from the databases
        """
        for i in range(0,self.combobox_mz.count()):
            self.combobox_mz.removeItem(0)
        for i in range(0, len(self.metabolites)):
            self.combobox_mz.addItem(list(self.metabolites)[i])
            
    def display_description(self, mz):
        """
        Adds the description of the metabolite to the label
        
        Parameters
        ----------
        mz : String
            m/z of the currently selected metabolite
        """
        if mz == "":
            self.label_mz_annotation.setText("")
            self.label_mz_annotation.setToolTip("")
            return
        try:
            name = self.metabolites[str(mz)][0]
        except ValueError:
            return
        self.label_mz_annotation.setText(name)
        description = self.metabolites[str(mz)][1]
        self.label_mz_annotation.setToolTip(description)
        
        
    def filter_mzs(self):
        """
        Filters the metabolites' m/z values displayed in the self.combobox_mz to display only those
        matching the filter_text. Checks m/z value, name and description.
        """
        filter_text = self.lineedit_mz_filter.text()
        self.combobox_mz.clear()
        for entry in self.metabolites:
            if (
                filter_text in str(entry)
                or filter_text in self.metabolites[str(entry)][0]
                or filter_text in self.metabolites[str(entry)][1]
                ):
                self.combobox_mz.addItem(entry)
            
            
    def display_image_from_plot(self):
        """
        Displays image of the currently displayed m/z range in the plot
        """
        if not hasattr(self, 'displayed_data'):
            return
        tolerance = self.displayed_data[-1,0] - self.displayed_data[0,0]
        mz = (self.displayed_data[0,0] + self.displayed_data[-1,0]) / 2
        self.calculate_image(mz, tolerance)
            
    def sample_mean_spectrum(self):
        """
        Displays the sample mean spectrum in the graph view
        """
        self.update_plot(self.sample_mean_spectrum, position = "sample mean")
        
        if not "sample points" in self.viewer.layers:
            self.viewer.add_labels(self.ms_object.get_samplepoints(), name = "sample points")
        
    def calculate_true_mean_spectrum(self):
        """
        Calculates the true mean spectrum if necessary, then calls for the spectrum to be displayed
        """
    
        if not hasattr(self, 'true_mean_spectrum'):
            print('its doing it!')
            worker = get_true_mean_spec(self.ms_object)
            worker.returned.connect(self.display_true_mean_spectrum)
            worker.start()
        else:
            self.update_plot(self.true_mean_spectrum, position = "true mean")
        
    def display_true_mean_spectrum(self, spectrum):
        """
        Displays the true mean spectrum and writes it to variable
        
        Parameters
        ----------
        spectrum : list
            true mean spectrum
        """
        self.true_mean_spectrum = spectrum
        self.data_array = np.array(spectrum)
        self.displayed_data = self.data_array
        self.update_plot(spectrum, position = "true mean")
        
    def export_spectrum_data(self):
        """
        Exports the current spectrum data to csv
        """
        import csv
        
        """dialog = QFileDialog()
        file = dialog.getSaveFileName(filter = "*.csv")"""
        file = save_dialog(self, "*.csv")
        if file[0] == "":
            # No file path + name chosen
            return
        
        csvfile = open(file[0], 'w', newline='')
        writer = csv.writer(csvfile)
        writer.writerow(["m/z","intensity"])
        
        for i in range(len(self.displayed_data[0])):
            data = [self.displayed_data[0,i]]
            data.append(self.displayed_data[1,i])
            writer.writerow(data)
        csvfile.close()
        
    
    def export_spectrum_plot(self):
        """
        Exports the current spectrum as [insert file format here]
        """
        print("dummy for later")
        pass

    


        
        
        
