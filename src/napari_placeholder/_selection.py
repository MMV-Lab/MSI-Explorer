from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton,
                            QComboBox, QLineEdit)

class SelectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        
        ### QObjects
        
        # Labels
        placeholder = QLabel("This is a placeholder. This will be replaced by the graph later.")
        label_select_database = QLabel("Select database")
        label_mz = QLabel("m/z")
        label_range = QLabel("Range:")
        label_mode = QLabel("Mode")
        label_mz_annotation = QLabel("")
        
        # Buttons
        btn_reset_view = QPushButton("Reset")
        btn_display_current_view = QPushButton("Show image")
        btn_select_database = QPushButton("Select")
        
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
        visual_frame.layout().addWidget(placeholder)
        
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
        