from msi_explorer import MetadataWindow, napari_get_reader

filename = 'src/msi_explorer/_tests/data/Example_Processed.imzML'
reader = napari_get_reader(filename)
maldi_data = reader(filename)

def test_metadata_expansion_key(make_napari_viewer):
    
    # Create metadata window
    my_window = MetadataWindow(maldi_data,None)
    
    # Fill "key" field of last line
    all_lines = my_window.layout().itemAt(0).widget().layout()
    last_line = all_lines.itemAt(all_lines.count() - 1).widget()
    last_line.layout().itemAt(0).widget().setText("Key")
    
    # Check if new line has been created
    all_lines = my_window.layout().itemAt(0).widget().layout()
    new_last_line = all_lines.itemAt(all_lines.count() - 1).widget()
    assert new_last_line.layout().itemAt(0).widget().text() != "Key"
    
def test_metadata_expansion_value(make_napari_viewer):
    
    # Create metadata window
    my_window = MetadataWindow(maldi_data,None)
    
    # Fill "value" field of last line
    all_lines = my_window.layout().itemAt(0).widget().layout()
    last_line = all_lines.itemAt(all_lines.count() - 1).widget()
    last_line.layout().itemAt(1).widget().setText("Value")
    
    # Check if new line has been created
    all_lines = my_window.layout().itemAt(0).widget().layout()
    new_last_line = all_lines.itemAt(all_lines.count() - 1).widget()
    assert new_last_line.layout().itemAt(1).widget().text() != "Value"
    
def test_metadata_expansion_both(make_napari_viewer):
    
    # Create metadata window
    my_window = MetadataWindow(maldi_data,None)
    
    # Fill "key" and "value" fields of last line
    all_lines = my_window.layout().itemAt(0).widget().layout()
    last_line = all_lines.itemAt(all_lines.count() - 1).widget()
    last_line.layout().itemAt(0).widget().setText("Key")
    last_line.layout().itemAt(1).widget().setText("Value")
    
    # Check if new line has been created
    all_lines = my_window.layout().itemAt(0).widget().layout()
    new_last_line = all_lines.itemAt(all_lines.count() - 1).widget()
    assert (new_last_line.layout().itemAt(0).widget().text() != "Key"
            and new_last_line.layout().itemAt(1).widget().text() != "Value")
