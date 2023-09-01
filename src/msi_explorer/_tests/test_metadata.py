from qtpy.QtWidgets import QLabel
from msi_explorer import MetadataWindow, napari_get_reader

filename = 'src/msi_explorer/_tests/data/Example_Processed.imzML'
reader = napari_get_reader(filename)
maldi_data = reader(filename)

def test_metadata_expansion_key(make_napari_viewer):
    
    # Create metadata window
    my_window = MetadataWindow(maldi_data,None)
    
    # Fill "key" field of last line
    data_frame = my_window.layout().itemAt(0).widget()
    data_frame.cellWidget(data_frame.rowCount() - 1, 0).setText("Key")
    
    # Check if new line has been created
    assert data_frame.cellWidget(data_frame.rowCount() - 1, 0).text() != "Key"
    
def test_metadata_expansion_value(make_napari_viewer):
    
    # Create metadata window
    my_window = MetadataWindow(maldi_data,None)
    
    # Fill "value" field of last line
    data_frame = my_window.layout().itemAt(0).widget()
    data_frame.cellWidget(data_frame.rowCount() - 1, 1).setText("Value")
    
    # Check if new line has been created
    assert data_frame.cellWidget(data_frame.rowCount() - 1, 1).text() != "Value"
    
def test_metadata_expansion_both(make_napari_viewer):
    
    # Create metadata window
    my_window = MetadataWindow(maldi_data,None)
    
    # Fill "key" and "value" fields of last line
    data_frame = my_window.layout().itemAt(0).widget()
    row = data_frame.rowCount() - 1
    data_frame.cellWidget(row, 0).setText("Key")
    data_frame.cellWidget(row, 1).setText("Value")
    
    # Check if new line has been created
    row = data_frame.rowCount() - 1
    assert data_frame.cellWidget(row, 0).text() != "Key" and data_frame.cellWidget(row, 1).text() != "Value"
